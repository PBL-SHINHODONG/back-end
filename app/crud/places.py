from typing import List, Optional, Union

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from app.schemas.places import (
    BasicPlaceInfoResponse,
    PlaceDetailsResponse, 
    CoordinatesResponse,
    NaverPlaceInfoResponse,
    KakaoPlaceInfoResponse
)
from app.models.places import Place, NaverPlace, KakaoPlace

def get_place_by_id(session: Session, place_id: int) -> Optional[PlaceDetailsResponse]:
    place = session.query(Place).filter(Place.id == place_id).first()
    return get_place_details(session, place)


def get_naver_place_info(session: Session, place_id: int) -> Optional[NaverPlaceInfoResponse]:
    naver_place = session.query(NaverPlace).filter(NaverPlace.place_id == place_id).first()
    return NaverPlaceInfoResponse(
        street_address=naver_place.street_address,
        category=naver_place.category,
        score=naver_place.score,
        review_count=naver_place.review_count
    ) if naver_place else None


def get_kakao_place_info(session: Session, place_id: int) -> Optional[KakaoPlaceInfoResponse]:
    kakao_place = session.query(KakaoPlace).filter(KakaoPlace.place_id == place_id).first()
    return KakaoPlaceInfoResponse(
        street_address=kakao_place.street_address,
        category=kakao_place.category,
        score=kakao_place.score,
        review_count=kakao_place.review_count
    ) if kakao_place else None


def get_place_by_name(session: Session, place_name: str) -> Optional[PlaceDetailsResponse]:
    place = session.query(Place).filter(Place.name == place_name).first()
    return get_place_details(session, place)


def get_places(
    session: Session, 
    sort_by: Union[str, None], 
    order: Optional[str],
    offset: int, 
    limit: int,
) -> List[PlaceDetailsResponse]:
    query = session.query(Place)
    if sort_by and sort_by in ["name", "score", "review_count"]:    
        query = query.order_by(desc(getattr(Place, sort_by))) if order == "desc" else query.order_by(asc(getattr(Place, sort_by)))
    places = query.offset(offset).limit(limit).all()
    return [get_place_details(session, place) for place in places]


def get_place_coordinate(session: Session, place_id: int) -> Optional[CoordinatesResponse]:
    coordinate = session.query(Place.pos_x, Place.pos_y).filter(Place.id == place_id).first()
    if coordinate:
        return CoordinatesResponse(pos_x=coordinate.pos_x, pos_y=coordinate.pos_y)
    return None


def get_place_details(session: Session, place: Place) -> Optional[PlaceDetailsResponse]:
    if not place:
        return None
    
    naver_info = get_naver_place_info(session, place.id)
    kakao_info = get_kakao_place_info(session, place.id)

    return PlaceDetailsResponse(
        basic_info=BasicPlaceInfoResponse(
            name=place.name,
            address=place.address,
            street_address=place.street_address,
            category=place.category,
            coordinates={"pos_x": place.pos_x, "pos_y": place.pos_y}
        ),
        naver_info=naver_info if naver_info else None,
        kakao_info=kakao_info if kakao_info else None
    )


def get_place_recommend(session: Session) -> PlaceDetailsResponse:
    return None
