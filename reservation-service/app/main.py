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
    user_consumer = RabbitMQConsumer(user_consuming_manager, user_created, 'user', ['created', 'updated', 'deleted'])
    reservation_consumer = RabbitMQConsumer(reservation_consuming_manager, activity_created, 'activity', ['created', 'updated', 'deleted', 'cancelled'])
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



def user_created(ch, method, properties, body):
    logger.info(f"Message recieved")
    logger.info(f"Method:{method}")
    logger.info(f"Properties:{properties}")
    logger.info(f"Body:{body}")
    user = parse_user_message(body)
    save_user(user)
    logger.info(f"User {user.username} added to the database")


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


def activity_created(ch, method, properties, body):
    logger.info(f"Message recieved")
    logger.info(f"Method:{method}")
    logger.info(f"Properties:{properties}")
    logger.info(f"Body:{body}")
    activity = parse_activity_message(body)
    save_activity(activity)
    logger.info(f"Activity {activity.name} added to the database")


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
        from_date_dt = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%S%z")
        query = query.filter(Reservation.date >= from_date_dt)

    if to_date is not None:
        to_date_dt = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%S%z")
        query = query.filter(Reservation.date <= to_date_dt)
    else:
        filtered_reservations = query.all()
    if len(filtered_reservations) == 0:
        raise HTTPException(status_code=404, detail="No activities found")
    return [ReservationDTO.model_validate(reservation) for reservation in filtered_reservations]


@app.post("/reservations/")
def create(reservation: ReservationDTO, db: Session = Depends(get_db)):
    if reservation is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
    if reservation.participant_id is None or reservation.activity_id is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    db_reservation = Reservation(
        participant_id=reservation.participant_id,
        activity_id=reservation.activity_id
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    dto = ReservationDTO(
        participant_id=db_reservation.participant_id,
        activity_id=db_reservation.activity_id,
        date=db_reservation.date.strftime("%Y-%m-%d %H:%M:%S")
    )
    publisher.publish(dto.model_dump_json(), 'created')
    return dto

@app.delete("/reservations/{reservation_id}")
def delete(reservation_id: int, db: Session = Depends(get_db)):
    if reservation_id is None:
        raise HTTPException(status_code=400, detail="Reservation ID is required")
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
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
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    db_reservation.participant_id = reservation.participant_id
    db_reservation.activity_id = reservation.activity_id
    db_reservation.date = datetime.strptime(reservation.date, "%Y-%m-%dT%H:%M:%S%z")
    db.commit()
    db.refresh(db_reservation)
    dto = ReservationDTO(
        participant_id=db_reservation.participant_id,
        activity_id=db_reservation.activity_id,
        date=db_reservation.date.strftime("%Y-%m-%dT%H:%M:%S%z")
    )
    print(dto.model_dump_json())
    publisher.publish(dto.model_dump_json(), 'updated')
    return dto

