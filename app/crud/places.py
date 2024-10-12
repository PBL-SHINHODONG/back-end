from typing import List, Optional, Union

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from app.schemas.places import PlaceResponse, PlaceCordinateResponse
from app.models.places import Place

def get_place_by_id(session: Session, place_id: int) -> PlaceResponse:
    return session.query(Place).filter(Place.id == place_id).first()

def get_place_by_name(session: Session, place_name: str) -> PlaceResponse:
    return session.query(Place).filter(Place.name == place_name).first()

def get_places(
    session: Session, 
    sort_by: Union[str, None], 
    order: Optional[str],
) -> List[PlaceResponse]:
    query = session.query(Place)
    if sort_by and sort_by in ["name", "score", "review_count"]:    
        query = query.order_by(desc(getattr(Place, sort_by))) if order == "desc" else query.order_by(asc(getattr(Place, sort_by)))
    return query.all()

def get_place_coordinate(session: Session, place_id: int) -> PlaceCordinateResponse:
    return session.query(Place.pos_x, Place.pos_y).filter(Place.id == place_id).first()

def get_place_recommend(session: Session) -> PlaceResponse:
    return None
