from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page, Params, paginate, add_pagination

from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.reviews import (
    ReviewResponse, 
    ReviewsCreateRequest
)
from app.crud import reviews

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    responses={404: {"description": "Not found"}},
)
add_pagination(router)


@router.get("/{place_id}", response_model=Page[ReviewResponse])
async def get_review_by_id(
    place_id: int, 
    params: Params = Depends(),
    db: Session = Depends(get_db)
):
    review = reviews.get_review_by_id(db, place_id)
    if not review:
        raise HTTPException(status_code=404, detail="review not found")
    return paginate(review, params)


@router.post("/")
async def create_review(review: ReviewsCreateRequest, db: Session = Depends(get_db)):
    new_review = reviews.create_review(db, review)
    return new_review


@router.delete("/{review_id}", status_code=204)
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    success = reviews.delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"detail": "Review deleted successfully"}
