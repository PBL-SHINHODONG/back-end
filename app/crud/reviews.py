from typing import Optional

from sqlalchemy.orm import Session

from app.schemas.reviews import (
    ReviewResponse, 
    ReviewsCreateRequest
)
from app.models.reviews import Review
from app.models.places import Place


def get_review_by_id(db: Session, place_id: int) -> Optional[ReviewResponse]:
    return db.query(Review).filter(Review.place_id == place_id).all()


def create_review(db: Session, review: ReviewsCreateRequest) -> Optional[ReviewResponse]:
    new_review = Review(
        place_id=review.place_id,
        user_id=review.user_id,
        comment=review.comment,
        score=review.score,
    )

    place = db.query(Place).filter(Place.id == review.place_id).first()
    place.reviews += 1

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return ReviewResponse.model_validate(new_review)


def delete_review(db: Session, review_id: int) -> bool:
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if review:
        db.delete(review)
        db.commit()
        return True
    return False
