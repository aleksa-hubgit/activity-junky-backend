# TODO: Implement the subscription service

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
from models import SubscriptionDTO, User, UserType, Subscription, SubscriptionMessage
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
    publishing_manager = RabbitMQConnectionManager(config)
    user_consumer = RabbitMQConsumer(user_consuming_manager, user_created, 'user', ['created', 'updated', 'deleted'])
    publisher = RabbitMQPublisher(publishing_manager, 'subscription')
    user_consumer.start_consuming()
    try:
        yield
    finally:
        logger.info('Closing connection')
        user_consuming_manager.close()
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


@app.post("/subscriptions/subscribe/{organizer}/{username}")
async def create_subscription(organizer: str, username, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    organizer = db.query(User).filter(User.username == organizer).first()
    if organizer is None:
        raise HTTPException(status_code=404, detail="Organizer not found")
    subscription = Subscription(participant_id=user.id, organizer_id=organizer.id, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    message = SubscriptionMessage(
        id=subscription.id,
        participant_id=subscription.participant_id,
        organizer_id=subscription.organizer_id,
        date=subscription.date,
    )
    publisher.publish(message.model_dump_json(), 'created')
    return SubscriptionDTO(
        participant=user.username, 
        organizer=organizer.username, 
        date=subscription.date
    )

@app.get("/subscriptions/{username}")
async def get_subscriptions(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    subscriptions = db.query(Subscription).filter(Subscription.participant_id == user.id).all()
    subs = []
    for subscription in subscriptions:
        organizer = db.query(User).filter(User.id == subscription.organizer_id).first()
        if organizer is None:
            raise HTTPException(status_code=500, detail="Organizer not found")
        subs.append(SubscriptionDTO(participant=user.username, organizer=organizer.username, date=subscription.date))
    return subs

@app.post("/subscriptions/cancel/{organizer}/{username}")
async def cancel_subscription(organizer: str, username: str, db: Session = Depends(get_db)):
    subscription = (
        db.query(Subscription)
        .join(User, Subscription.participant_id == User.id)
        .join(User, Subscription.organizer_id == User.id)
        .filter(User.username == username, User.username == organizer)
        .first()
    )
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    subscription.active = False
    db.commit()
    db.refresh(subscription)
    message = SubscriptionMessage(
        id=subscription.id,
        participant_id=subscription.participant_id,
        organizer_id=subscription.organizer_id,
        date=subscription.date,
    )
    publisher.publish(message.model_dump_json(), 'canceled')
    return {"message": "Subscription canceled"}

