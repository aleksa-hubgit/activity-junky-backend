from enum import Enum
import os
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String, Enum as SQLAlchemyEnum, create_engine
from sqlalchemy.ext.declarative import declarative_base



DATABASE_HOSTNAME=os.environ.get('DATABASE_HOSTNAME')
DATABASE_PORT=os.environ.get('DATABASE_PORT')
DATABASE_NAME=os.environ.get('DATABASE_NAME')
DATABASE_USERNAME=os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD=os.environ.get('DATABASE_PASSWORD')
DATABASE_URL=f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)

Base = declarative_base()


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer)
    organizer_id = Column(Integer)
    date = Column(String)
    active = Column(Boolean, default=True)


class SubscriptionMessage(BaseModel):
    id: int
    participant_id: int
    organizer_id: int
    date: str

    class Config:
        from_attributes = True

class SubscriptionDTO(BaseModel):
    participant: str
    organizer: str
    date: str

    class Config:
        from_attributes = True

class UserType(str, Enum):
    PARTICIPANT = "participant"
    ORGANIZER = "organizer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    user_type = Column(SQLAlchemyEnum(UserType))

Base.metadata.create_all(bind=engine)

