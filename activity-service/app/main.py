from contextlib import asynccontextmanager
import json
import os
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fuzzywuzzy import fuzz
from typing import List, Optional
from datetime import datetime
import logging
from models import Activity, User, Reservation, ActivityDTO, ActivityResponseDTO, ActivityStatus, UserType
from consumer import RabbitMQConsumer
from config import RabbitMQConnectionConfig
from connection_manager import RabbitMQConnectionManager
from publisher import RabbitMQPublisher

logging.basicConfig(level=logging.INFO, format='%(levelname)s:   %(message)s')
logger = logging.getLogger(__name__)
pika_logger = logging.getLogger("pika")
pika_logger.setLevel(logging.WARNING)


RABBITMQ_HOSTNAME = os.environ.get('RABBITMQ_HOSTNAME')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')
RABBITMQ_USERNAME = os.environ.get('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
DATABASE_URL = f"postgresql://{os.getenv('DATABASE_USERNAME')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOSTNAME')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app):
    global publisher
    logger.info("Waiting for RabbitMQ connection...")
    config = RabbitMQConnectionConfig(RABBITMQ_HOSTNAME, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    user_connection_manager = RabbitMQConnectionManager(config)
    reservation_connection_manager = RabbitMQConnectionManager(config)
    publisher_connection_manager = RabbitMQConnectionManager(config)
    publisher = RabbitMQPublisher(publisher_connection_manager, 'activity')
    user_consumer = RabbitMQConsumer(user_connection_manager, user_created, 'user', ['created'])
    reservation_consumer = RabbitMQConsumer(reservation_connection_manager, reservation_created, 'reservation', ['created'])
    user_consumer.start_consuming()
    reservation_consumer.start_consuming()
    try:
        yield
    finally:
        user_connection_manager.close()
        reservation_connection_manager.close()
        publisher_connection_manager.close()

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


def reservation_created(ch, method, properties, body):
    logger.info(f"Message received")
    logger.info(f"Method:{method}")
    logger.info(f"Properties:{properties}")
    logger.info(f"Body:{body}")
    reservation = parse_reservation_message(body)
    save_reservation(reservation)
    logger.info(f"Reservation {reservation.id} added to the database")


def save_reservation(reservation):
    db = next(get_db())
    try:
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding reservation to database: {e}")
    finally:
        db.close()


def parse_reservation_message(body):
    reservation_data = json.loads(body)
    return Reservation(
        participant_id=reservation_data['participant_id'],
        activity_id=reservation_data['activity_id'],
        date=datetime.strptime(reservation_data['date'], "%Y-%m-%dT%H:%M:%S%z")
    )




@app.get("/activities")
def read_activities(
    username: Optional[str] = None,
    user_id: Optional[int] = None,
    category: Optional[List[str]] = Query(None),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    from_price: Optional[float] = None,
    to_price: Optional[float] = None,
    search: Optional[str] = None,
    similarity_threshold: int = 70,
    db: Session = Depends(get_db),
    available: Optional[bool] = None,
    status: Optional[ActivityStatus] = None
):
    query = db.query(Activity)
    if username is not None:
        query = query.join(User, User.id == Activity.user_id).filter(User.username == username)
    if user_id is not None:
        query = query.filter(Activity.user_id == user_id)
    if category is not None:
        query = query.filter(Activity.category.in_(category))
    if from_date is not None:
        from_date_dt = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%S%z")
        query = query.filter(datetime.strptime(Activity.date, "%Y-%m-%dT%H:%M:%S%z") >= from_date_dt)
    if to_date is not None:
        to_date_dt = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%S%z")
        query = query.filter(datetime.strptime(Activity.date, "%Y-%m-%dT%H:%M:%S%z") <= to_date_dt)
    if from_price is not None:
        query = query.filter(Activity.price >= from_price)
    if to_price is not None:
        query = query.filter(Activity.price <= to_price)
    if available is not None:
        query = query.filter(Activity.total_places > 0)
    if status is not None:
        query = query.filter(Activity.status == status)
    if search is not None:
        activities = query.all()
        filtered_activities = list(filter(
            lambda x: fuzz.partial_ratio(search.lower(), x.name.lower()) >= similarity_threshold or 
                      fuzz.partial_ratio(search.lower(), x.description.lower()) >= similarity_threshold, 
            activities
        ))
    else:
        filtered_activities = query.all()
    if len(filtered_activities) == 0:
        return []
    for activity in filtered_activities:
        user = db.query(User).filter(User.id == activity.user_id).first()
        activity.username = user.username
    return [ActivityResponseDTO.model_validate(activity) for activity in filtered_activities]

@app.post("/activities")
def create(activity: ActivityDTO, db: Session = Depends(get_db)):
    if activity is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
    if  activity.category is None or activity.date is None or activity.price is None or activity.name is None or activity.description is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
    if activity.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    if activity.total_places < 0:
        raise HTTPException(status_code=400, detail="Total places cannot be negative")
    try :
        datetime.strptime(activity.date, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    user = db.query(User).filter(User.username == activity.username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User found: {user.username}")
    db_activity = Activity(
        user_id=user.id,
        category=activity.category,
        date=activity.date,
        price=activity.price,
        name=activity.name,
        description=activity.description,
        total_places=activity.total_places,
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    dto = ActivityResponseDTO(
        id=db_activity.id,
        category=db_activity.category,
        date=db_activity.date,
        price=db_activity.price,
        name=db_activity.name,
        description=db_activity.description,
        total_places=db_activity.total_places,
        status=db_activity.status,
        user_id=db_activity.user_id,
        username=user.username
    )
    publisher.publish(dto.model_dump_json(), 'created')
    return dto

@app.delete("/activities/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    if activity_id is None:
        raise HTTPException(status_code=400, detail="Activity ID is required")
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(db_activity)
    db.commit()
    publisher.publish(json.dumps({"activity_id": activity_id}), 'deleted')
    return {"message": "Activity deleted successfully"}

@app.put("/activities/{activity_id}")
def update_activity(activity_id: int, activity: ActivityDTO, db: Session = Depends(get_db)):
    if activity_id is None:
        raise HTTPException(status_code=400, detail="Activity ID is required")
    if activity is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
        
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    db_activity.user_id = activity.user_id
    db_activity.category = activity.category
    db_activity.date = activity.date
    db_activity.price = activity.price
    db_activity.name = activity.name
    db_activity.description = activity.description
    db_activity.total_places = activity.total_places
    db_activity.status = activity.status
    db.commit()
    db.refresh(db_activity)
    dto = ActivityResponseDTO(
        id=db_activity.id,
        category=db_activity.category,
        date=db_activity.date,
        price=db_activity.price,
        name=db_activity.name,
        description=db_activity.description,
        total_places=db_activity.total_places,
        status=db_activity.status,
        user_id=db_activity.user_id
    )
    publisher.publish(dto.model_dump_json(), 'updated')
    return dto

@app.put("/activities/cancel/{activity_id}")
def cancel_activity(activity_id: int, db: Session = Depends(get_db)):
    if activity_id is None:
        raise HTTPException(status_code=400, detail="Activity ID is required")
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    db_activity.status = ActivityStatus.CANCELED
    db.commit()
    db.refresh(db_activity)
    dto = ActivityResponseDTO(
        id=db_activity.id,
        category=db_activity.category,
        date=db_activity.date,
        price=db_activity.price,
        name=db_activity.name,
        description=db_activity.description,
        total_places=db_activity.total_places,
        status=db_activity.status,
        user_id=db_activity.user
    )
    publisher.publish(dto.model_dump_json(), 'cancelled')
    return {"message": "Activity canceled successfully"}

@app.put("/activities/{activity_id}")
def finish_activity(activity_id: int, db: Session = Depends(get_db)):
    if activity_id is None:
        raise HTTPException(status_code=400, detail="Activity ID is required")
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    db_activity.status = ActivityStatus.FINISHED
    db.commit()
    db.refresh(db_activity)
    dto = ActivityResponseDTO(
        id=db_activity.id,
        category=db_activity.category,
        date=db_activity.date,
        price=db_activity.price,
        name=db_activity.name,
        description=db_activity.description,
        total_places=db_activity.total_places,
        status=db_activity.status,
        user_id=db_activity.user
    )
    publisher.publish(dto.model_dump_json(), 'finished')
    return {"message": "Activity finished successfully"}
    