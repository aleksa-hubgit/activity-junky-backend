import os
from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fuzzywuzzy import fuzz
from typing import List, Optional
from datetime import datetime

DATABASE_HOSTNAME=os.environ.get('DATABASE_HOSTNAME')
DATABASE_PORT=os.environ.get('DATABASE_PORT')
DATABASE_NAME=os.environ.get('DATABASE_NAME')
DATABASE_USERNAME=os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD=os.environ.get('DATABASE_PASSWORD')
DATABASE_URL=f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class ReviewDTO(BaseModel):
    text: str
    rating: int
    reviewer: int
    reviewee: int
    date: str

    class Config:
        from_attributes = True


class ActivityReviewDTO(BaseModel):
    text: str
    rating: int
    reviewer: int
    activity_id: int
    date: str

    class Config:
        from_attributes = True

class ActivityReview(Base):
    __tablename__ = "activity_reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer = Column(Integer)
    text = Column(String)
    rating = Column(Integer)
    activity_id = Column(Integer)
    date = Column(Date)

# SQLAlchemy model
class UserReview(Base):
    __tablename__ = "user_reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer = Column(Integer)
    text = Column(String)
    rating = Column(Integer)
    reviewee = Column(Integer)
    date = Column(Date)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/reviews/user")
def read(
    reviewer: Optional[int] = None,
    reviewee: Optional[int] = None,
    from_rating: Optional[int] = None,
    to_rating: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    search: Optional[str] = None,
    similarity_threshold: int = 70,
    db: Session = Depends(get_db)
):
    query = db.query(UserReview)

    # Filter by user_id
    if reviewer is not None:
        query = query.filter(UserReview.reviewer == reviewer)

    # Filter by multiple categories
    if reviewee is not None:
        query = query.filter(UserReview.reviewee == reviewee)

    # Filter by date range
    if from_date is not None:
        from_date_dt = datetime.strptime(from_date, "%Y-%m-%d")
        query = query.filter(UserReview.date >= from_date_dt)

    if to_date is not None:
        to_date_dt = datetime.strptime(to_date, "%Y-%m-%d")
        query = query.filter(UserReview.date <= to_date_dt)

    # Filter by price range
    if from_rating is not None:
        query = query.filter(UserReview.rating >= from_rating)

    if to_rating is not None:
        query = query.filter(UserReview.rating <= to_rating)

    # Fuzzy search in name and description
    if search is not None:
        reviews = query.all()
        filtered_reviews = list(filter(
            lambda x: fuzz.partial_ratio(search.lower(), x.text.lower()) >= similarity_threshold, 
            reviews
        ))
    else:
        filtered_reviews = query.all()

    return [ReviewDTO.model_validate(review) for review in filtered_reviews]


# ovo treba da publishuje event UserReviewCreated koji se prima od strane Notification servisa i onda notification servis tipa preko websocketa salje notifikaciju korisnicima
@app.post("/reviews/user")
def create(review: ReviewDTO, db: Session = Depends(get_db)):
    db_review = UserReview(
        reviewer=review.reviewer,
        reviewee=review.reviewee,
        date=datetime.strptime(review.date, "%Y-%m-%d"),
        rating=review.rating,
        text=review.text,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    # TODO: Publish event UserReviewCreated
    return review


# ovo treba da publishuje event UserReviewDeleted koji se prima od strane Notification servisa
@app.delete("/reviews/user/{review_id}")
def delete(review_id: int, db: Session = Depends(get_db)):
    db_review = db.query(UserReview).filter(UserReview.id == review_id).first()
    db.delete(db_review)
    db.commit()
    return {"message": f"Review with id: [{review_id}] deleted successfully"}



@app.put("/reviews/user/{review_id}")
def update(review_id: int, review: ReviewDTO, db: Session = Depends(get_db)):
    db_review = db.query(UserReview).filter(UserReview.id == review_id).first()
    db_review.reviewer = review.reviewer
    db_review.reviewee = review.reviewee
    db_review.date = datetime.strptime(review.date, "%Y-%m-%d")
    db_review.rating = review.rating
    db_review.text = review.text
    db.commit()
    db.refresh(db_review)
    return review



@app.get("/reviews/activity")
def read(
    reviewer: Optional[int] = None,
    activity_id: Optional[int] = None,
    from_rating: Optional[int] = None,
    to_rating: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    search: Optional[str] = None,
    similarity_threshold: int = 70,
    db: Session = Depends(get_db)
):
    query = db.query(ActivityReview)

    # Filter by user_id
    if reviewer is not None:
        query = query.filter(ActivityReview.reviewer == reviewer)

    # Filter by multiple categories
    if activity_id is not None:
        query = query.filter(ActivityReview.activity_id == activity_id)

    # Filter by date range
    if from_date is not None:
        from_date_dt = datetime.strptime(from_date, "%Y-%m-%d")
        query = query.filter(ActivityReview.date >= from_date_dt)

    if to_date is not None:
        to_date_dt = datetime.strptime(to_date, "%Y-%m-%d")
        query = query.filter(ActivityReview.date <= to_date_dt)

    # Filter by price range
    if from_rating is not None:
        query = query.filter(ActivityReview.rating >= from_rating)

    if to_rating is not None:
        query = query.filter(ActivityReview.rating <= to_rating)

    # Fuzzy search in name and description
    if search is not None:
        reviews = query.all()
        filtered_reviews = list(filter(
            lambda x: fuzz.partial_ratio(search.lower(), x.text.lower()) >= similarity_threshold, 
            reviews
        ))
    else:
        filtered_reviews = query.all()

    return [ActivityReviewDTO.model_validate(review) for review in filtered_reviews]


# ovo treba da publishuje event ActivityReviewCreated koji se prima od strane Notification servisa
@app.post("/reviews/activity")
def create(review: ActivityReviewDTO, db: Session = Depends(get_db)):
    db_review = ActivityReview(
        reviewer=review.reviewer,
        activity_id=review.activity_id,
        date=datetime.strptime(review.date, "%Y-%m-%d"),
        rating=review.rating,
        text=review.text,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    # TODO: Publish event ActivityReviewCreated
    return review


# ovo treba da publishuje event ActivityReviewDeleted koji se prima od strane Notification servisa
@app.delete("/reviews/activity/{review_id}")
def delete(review_id: int, db: Session = Depends(get_db)):
    db_review = db.query(ActivityReview).filter(ActivityReview.id == review_id).first()
    db.delete(db_review)
    db.commit()
    return {"message": f"Review with id: [{review_id}] deleted successfully"}



@app.put("/reviews/activity/{review_id}")
def update(review_id: int, review: ActivityReviewDTO, db: Session = Depends(get_db)):
    db_review = db.query(ActivityReview).filter(ActivityReview.id == review_id).first()
    db_review.reviewer = review.reviewer
    db_review.activity_id = review.activity_id
    db_review.date = datetime.strptime(review.date, "%Y-%m-%d")
    db_review.rating = review.rating
    db_review.text = review.text
    db.commit()
    db.refresh(db_review)
    return review

# ovo treba da publishuje event ActivityReviewsDeleted koji se prima od strane Activity servisa
# i da se pokrece kada se pozove delete na /activities/{activity_id} odnosno da je subscriber na event StartActivityDelete
@app.delete("/reviews/activity/{activity_id}")
def delete_reviews_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = db.query(ActivityReview).filter(ActivityReview.activity_id == activity_id).first()
    db.delete(db_activity)
    db.commit()
    return {"message": f"Activity reviews with id: [{activity_id}] deleted successfully"}

# ovo treba da publishuje event UserReviewsDeleted koji se prima od strane User servisa
# i da se pokrece kada se pozove delete na /users/{user_id} odnosno da je subscriber na event StartUserDelete
@app.delete("/reviews/user/{user_id}")
def delete_reviews_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserReview).filter(UserReview.reviewee == user_id).first()
    db.delete(db_user)
    db.commit()
    return {"message": f"User reviews with id: [{user_id}] deleted successfully"}

