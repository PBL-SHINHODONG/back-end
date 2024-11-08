from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page, Params, paginate, add_pagination

from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.visitedplaces import VisitedPlaceCreateRequest, VisitedPlaceResponse

from app.schemas.places import PlaceDetailsResponse
from app.crud import visitedplaces

router = APIRouter(
    prefix="/visited_places",
    tags=["visited_places"],
    responses={404: {"description": "Not found"}},
)
add_pagination(router)


@router.post("/visit", response_model=VisitedPlaceResponse)
async def add_visited_place(place: VisitedPlaceCreateRequest, db: Session = Depends(get_db)):
    visited_place = visitedplaces.add_visited_place(db, place)
    return visited_place


@router.get("/{user_id}", response_model=Page[PlaceDetailsResponse])
async def get_visited_place(user_id: int, params: Params = Depends(), db: Session = Depends(get_db)):
    visited_places = visitedplaces.get_visited_place_by_user(db, user_id)
    if not visited_places:
        raise HTTPException(status_code=404, detail="No visited places found for this user")
    return paginate(visited_places, params)
