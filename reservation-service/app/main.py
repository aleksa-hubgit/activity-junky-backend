from contextlib import asynccontextmanager
import json
import os
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime
import logging
from consumer import RabbitMQConsumer
from publisher import RabbitMQPublisher
from models import Activity, Reservation, ReservationDTO, User, UserType
from connection_manager import RabbitMQConnectionManager
from config import RabbitMQConnectionConfig
logging.basicConfig(level=logging.INFO, format='%(levelname)s:   %(message)s')
logger = logging.getLogger(__name__)
pika_logger = logging.getLogger("pika")
pika_logger.setLevel(logging.WARNING)


RABBITMQ_HOSTNAME=os.environ.get('RABBITMQ_HOSTNAME')
RABBITMQ_PORT=os.environ.get('RABBITMQ_PORT')
RABBITMQ_USERNAME=os.environ.get('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD=os.environ.get('RABBITMQ_PASSWORD')
DATABASE_URL = f"postgresql://{os.getenv('DATABASE_USERNAME')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOSTNAME')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

publisher = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app):
    global publisher
    config = RabbitMQConnectionConfig(RABBITMQ_HOSTNAME, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    user_consuming_manager = RabbitMQConnectionManager(config)
    reservation_consuming_manager = RabbitMQConnectionManager(config)
    publishing_manager = RabbitMQConnectionManager(config)
    user_consumer = RabbitMQConsumer(user_consuming_manager, user_callback, 'user', ['created', 'updated', 'deleted'])
    reservation_consumer = RabbitMQConsumer(reservation_consuming_manager, activity_callback, 'activity', ['created', 'updated', 'deleted', 'cancelled'])
    publisher = RabbitMQPublisher(publishing_manager, 'reservation')
    user_consumer.start_consuming()
    reservation_consumer.start_consuming()
    try:
        yield
    finally:
        user_consuming_manager.close()
        reservation_consuming_manager.close()
        publishing_manager.close()

app = FastAPI(lifespan=lifespan)



def user_callback(ch, method, properties, body):
    logger.info(f"Message recieved")
    logger.info(f"Method:{method}")
    logger.info(f"Properties:{properties}")
    user = parse_user_message(body)
    if method.routing_key == 'created':
        logger.info(f"User created")
        save_user(user)
    elif method.routing_key == 'updated':
        logger.info(f"User updated")
        update_user(user)
    elif method.routing_key == 'deleted':
        logger.info(f"User deleted")
        delete_user(user)


def delete_user(user):
    db = next(get_db())
    try:
        db.query(User).filter(User.id == user.id).delete()
        reservation = db.query(Reservation).filter(Reservation.participant_id == user.id).delete()
        dto = ReservationDTO(
            participant_id=reservation.participant_id,
            activity_id=reservation.activity_id,
            date=reservation.date
        )
        db.query(Reservation).filter(Reservation.participant_id == user.id).delete()
        db.commit()
        publisher.publish(dto.model_dump_json(), 'deleted')
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user from database: {e}")
    finally:
        db.close()


def update_user(user):
    db = next(get_db())
    try:
        db.query(User).filter(User.id == user.id).update({User.username: user.username, User.email: user.email, User.user_type: user.user_type})
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user in database: {e}")
    finally:
        db.close()


def save_user(user):
    db = next(get_db())
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding user to database: {e}")
    finally:
        db.close()


def parse_user_message(body):
    user_data = json.loads(body)
    return User(id = user_data['id'],username=user_data['username'], email=user_data['email'], user_type=UserType(user_data['user_type']))


def activity_callback(ch, method, properties, body):
    logger.info(f"Message recieved")
    logger.info(f"Method:{method}")
    logger.info(f"Properties:{properties}")
    activity = parse_activity_message(body)
    if method.routing_key == 'created':
        logger.info(f"Activity created")
        save_activity(activity)
    elif method.routing_key == 'updated':
        logger.info(f"Activity updated")
        update_activity(activity)
    elif method.routing_key == 'deleted':
        logger.info(f"Activity deleted")
        delete_activity(activity)

def delete_activity(activity):
    db = next(get_db())
    try:
        db.query(Activity).filter(Activity.id == activity.id).delete()
        db.query(Reservation).filter(Reservation.activity_id == activity.id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting activity from database: {e}")
    finally:
        db.close()


def update_activity(activity):
    db = next(get_db())
    try:
        db.query(Activity).filter(Activity.id == activity.id).update({Activity.user_id: activity.user_id, Activity.category: activity.category, Activity.date: activity.date, Activity.price: activity.price, Activity.name: activity.name})
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating activity in database: {e}")
    finally:
        db.close()


def save_activity(activity):
    db = next(get_db())
    try:
        db.add(activity)
        db.commit()
        db.refresh(activity)
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding activity to database: {e}")
    finally:
        db.close()


def parse_activity_message(body):
    activity_data = json.loads(body)
    return Activity(id = activity_data['id'],user_id=activity_data['user_id'], category=activity_data['category'], date=activity_data['date'], price=activity_data['price'], name=activity_data['name'])


@app.get("/reservations/")
def read(
    participant_id: Optional[int] = None,
    activity_id: Optional[List[str]] = Query(None),
    participant: Optional[str] = None,
    organizer: Optional[str] = None,
    activity_name: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Reservation)


    if participant_id is not None:
        query = query.filter(Reservation.participant_id == participant_id)

    # Filter by multiple categories
    if activity_id is not None:
        query = query.filter(Reservation.activity_id == activity_id)

    # Filter by date range
    if from_date is not None:
        from_date_dt = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%S")
        query = query.filter(Reservation.date >= from_date_dt)

    if to_date is not None:
        to_date_dt = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%S")
        query = query.filter(Reservation.date <= to_date_dt)
    else:
        filtered_reservations = query.all()
    if len(filtered_reservations) == 0:
        raise HTTPException(status_code=400, detail="No activities found")
    return [ReservationDTO.model_validate(reservation) for reservation in filtered_reservations]

@app.get("/reservations/{participant_username}")
def read(participant_username: str, db: Session = Depends(get_db)):
    participant = db.query(User).filter(User.username == participant_username).first()
    if participant is None:
        raise HTTPException(status_code=400, detail="Participant not found")
    reservations = db.query(Reservation).filter(Reservation.participant_id == participant.id).all()
    if len(reservations) == 0:
        raise HTTPException(status_code=400, detail="No reservations found")
    dtos = []
    for reservation in reservations:
        activity = db.query(Activity).filter(Activity.id == reservation.activity_id).first()
        if activity is None:
            raise HTTPException(status_code=400, detail="Activity not found")
        organizer = db.query(User).filter(User.id == activity.user_id).first()
        if organizer is None:
            raise HTTPException(status_code=400, detail="Organizer not found")
        dto = ReservationDTO(
            participant_id=reservation.participant_id,
            activity_id=reservation.activity_id,
            participant_username=participant_username,
            activity_name=activity.name,
            category=activity.category,
            price=activity.price,
            organizer=organizer.username,
            date=reservation.date,
            id=reservation.id
        )
        dtos.append(dto)
    return dtos

@app.post("/reservations/")
def create(reservation: ReservationDTO, db: Session = Depends(get_db)):
    if reservation is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
    if reservation.participant_username is None or reservation.activity_id is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
    participant = db.query(User).filter(User.username == reservation.participant_username).first()
    activity = db.query(Activity).filter(Activity.id == reservation.activity_id).first()
    if participant is None:
        raise HTTPException(status_code=400, detail="Participant not found")
    if activity is None:
        raise HTTPException(status_code=400, detail="Activity not found")
    logger.info("Participant and activity found")
    reservation_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    logger.info(f"Reservation date: {reservation_date}")
    logger.info(f"Reservation date type: {type(reservation_date)}")
    db_reservation = Reservation(
        participant_id=participant.id,
        activity_id=reservation.activity_id,
        date=reservation_date
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    logger.info("Reservation added to the database")
    logger.info(f"Participant ID: {db_reservation.participant_id}")
    logger.info(f"Activity ID: {db_reservation.activity_id}")
    logger.info(f"Date: {db_reservation.date}")
    logger.info(f"Date object type:{type(db_reservation.date)}")
    logger.info(f"Participant username: {reservation.participant_username}")
    dto = ReservationDTO(
        participant_id=db_reservation.participant_id,
        activity_id=db_reservation.activity_id,
        participant_username=reservation.participant_username,
        date=db_reservation.date
    )
    logger.info("Created dto")
    publisher.publish(dto.model_dump_json(), 'created')
    return dto

@app.delete("/reservations/{reservation_id}")
def delete(reservation_id: int, db: Session = Depends(get_db)):
    if reservation_id is None:
        raise HTTPException(status_code=400, detail="Reservation ID is required")
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if reservation is None:
        raise HTTPException(status_code=400, detail="Reservation not found")
    db.delete(reservation)
    db.commit()
    publisher.publish(json.dumps({"reservation_id": reservation_id}), 'deleted')
    return {"message": "Reservation deleted successfully"}


@app.put("/reservation/{reservation_id}")
def update(reservation_id: int, reservation: ReservationDTO, db: Session = Depends(get_db)):
    if reservation_id is None:
        raise HTTPException(status_code=400, detail="Reservation ID is required")
    if reservation is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
        
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=400, detail="Reservation not found")
    
    user = db.query(User).filter(User.username == reservation.participant_username).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    db_reservation.participant_id = user.id
    db_reservation.activity_id = reservation.activity_id
    db.commit()
    db.refresh(db_reservation)
    dto = ReservationDTO(
        participant_id=db_reservation.participant_id,
        activity_id=db_reservation.activity_id,
        date=db_reservation.date
    )
    publisher.publish(dto.model_dump_json(), 'updated')
    return dto

@app.put("/reservations/cancel/{id}")
def cancel_reservation(id: int, db: Session = Depends(get_db)):
    if id is None:
        raise HTTPException(status_code=400, detail="Reservation ID is required")
    reservation = db.query(Reservation).filter(Reservation.id == id).first()
    if reservation is None:
        raise HTTPException(status_code=400, detail="Reservation not found")
    db.delete(reservation)
    db.commit()
    dto = ReservationDTO(
        participant_id=reservation.participant_id,
        activity_id=reservation.activity_id,
        date=reservation.date
    )
    publisher.publish(dto.model_dump_json(), 'cancelled')
    return {"message": "Reservation cancelled successfully"}

