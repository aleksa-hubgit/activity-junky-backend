from enum import Enum
import os
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Enum as SQLAlchemyEnum, create_engine
from sqlalchemy.ext.declarative import declarative_base



DATABASE_HOSTNAME=os.environ.get('DATABASE_HOSTNAME')
DATABASE_PORT=os.environ.get('DATABASE_PORT')
DATABASE_NAME=os.environ.get('DATABASE_NAME')
DATABASE_USERNAME=os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD=os.environ.get('DATABASE_PASSWORD')
DATABASE_URL=f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)

Base = declarative_base()

class ActivityStatus(str, Enum):
    AVAILABLE = "available"
    FINISHED = "finished"
    CANCELED = "canceled"


class UserType(str, Enum):
    PARTICIPANT = "participant"
    ORGANIZER = "organizer"


class ActivityDTO(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    category: str
    date: str
    price: float
    total_places: int
    status: ActivityStatus
    user_id: Optional[int] = None
    username: str


class ActivityResponseDTO(BaseModel):
    id: int
    category: str
    date: str
    price: float
    name: str
    total_places: int
    description: str
    status: ActivityStatus
    user_id: int
    username: str


    class Config:
        from_attributes = True


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer)
    activity_id = Column(Integer)
    date = Column(String)



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    user_type = Column(SQLAlchemyEnum(UserType))


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    category = Column(String)
    date = Column(String)
    price = Column(Float)
    name = Column(String)
    description = Column(String)
    total_places = Column(Integer)
    status = Column(SQLAlchemyEnum(ActivityStatus), default=ActivityStatus.AVAILABLE)


Base.metadata.create_all(bind=engine)