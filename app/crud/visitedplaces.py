from typing import Optional

from sqlalchemy.orm import Session

from app.models.visitedplaces import VisitedPlace
from app.schemas.visitedplaces import VisitedPlaceCreateRequest, VisitedPlaceResponse
from app.schemas.places import PlaceDetailsResponse
from app.crud.places import get_place_details

def add_visited_place(db: Session, place: VisitedPlaceCreateRequest) -> VisitedPlaceResponse:
    visited_place = db.query(VisitedPlace).filter_by(
        user_id=place.user_id, 
        place_id=place.place_id
    ).first()

    if visited_place:
        visited_place.visit_count += 1
    else:
        visited_place = VisitedPlace(
            place_id=place.place_id,
            user_id=place.user_id,
            visit_count=1
        )
        db.add(visited_place)
    
    db.commit()
    db.refresh(visited_place)
    return visited_place


def get_visited_place_by_user(db: Session, user_id: int) -> Optional[PlaceDetailsResponse]:
    visited_places = db.query(VisitedPlace).filter_by(user_id=user_id).all()
    return [get_place_details(db, visited_place.place) for visited_place in visited_places]
