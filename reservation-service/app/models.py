from enum import Enum
import os
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLAlchemyEnum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime



DATABASE_HOSTNAME=os.environ.get('DATABASE_HOSTNAME')
DATABASE_PORT=os.environ.get('DATABASE_PORT')
DATABASE_NAME=os.environ.get('DATABASE_NAME')
DATABASE_USERNAME=os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD=os.environ.get('DATABASE_PASSWORD')
DATABASE_URL=f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)

Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    category = Column(String)
    date = Column(DateTime)
    price = Column(Float)
    name = Column(String)
    description = Column(String)



class ReservationDTO(BaseModel):
    participant_id: int
    activity_id: int
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

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer)
    activity_id = Column(Integer)
    date = Column(DateTime, default=datetime.now)


Base.metadata.create_all(bind=engine)