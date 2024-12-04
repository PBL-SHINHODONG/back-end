from typing import List, Optional, Union

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.schemas.places import (
    BasicPlaceInfoResponse,
    PlaceDetailsResponse, 
    LatitudeLongitudeResponse,
    NaverPlaceInfoResponse,
    KakaoPlaceInfoResponse
)
from app.models.places import Place, NaverPlace, KakaoPlace
from app.models.users import User
from app.dependencies import toLatLng, getSeason, isWeekend

def get_place_by_id(db: Session, place_id: int) -> Optional[PlaceDetailsResponse]:
    place = db.query(Place).filter(Place.id == place_id).first()
    return get_place_details(db, place)


def get_naver_place_info(db: Session, place_id: int) -> Optional[NaverPlaceInfoResponse]:
    naver_place = db.query(NaverPlace).filter(NaverPlace.place_id == place_id).first()
    return NaverPlaceInfoResponse(
        street_address=naver_place.street_address,
        category=naver_place.subcategory,
        score=naver_place.score,
        review_count=naver_place.review_count
    ) if naver_place else None


def get_kakao_place_info(db: Session, place_id: int) -> Optional[KakaoPlaceInfoResponse]:
    kakao_place = db.query(KakaoPlace).filter(KakaoPlace.place_id == place_id).first()
    return KakaoPlaceInfoResponse(
        street_address=kakao_place.street_address,
        category=kakao_place.subcategory,
        score=kakao_place.score,
        review_count=kakao_place.review_count
    ) if kakao_place else None


def get_place_by_name(db: Session, place_name: str) -> Optional[PlaceDetailsResponse]:
    place = db.query(Place).filter(Place.name.ilike(place_name)).first()
    return get_place_details(db, place)


def get_places_by_name(
    db: Session, 
    order: Optional[str], 
    offset: int, 
    limit: int,
) -> List[PlaceDetailsResponse]:
    query = db.query(Place)
    query = query.order_by(desc(Place.name)) if order == "desc" else query.order_by(asc(Place.name))
    places = query.offset(offset).limit(limit).all()
    return [get_place_details(db, place) for place in places]


def get_places(
    db: Session, 
    sort_by: str,
    order: Optional[str] = "desc",
    offset: int = 0, 
    limit: int = 10,
) -> List[PlaceDetailsResponse]:
    if sort_by == "name":
        query = db.query(Place)
        query = query.order_by(desc(Place.name)) if order == "desc" else query.order_by(asc(Place.name))
    elif sort_by == "review_count":
        query = (
            db.query(
                Place,
                func.greatest(
                    func.coalesce(NaverPlace.review_count, 0),
                    func.coalesce(KakaoPlace.review_count, 0)
                ).label("max_review_count")
            )
            .join(NaverPlace, Place.id == NaverPlace.place_id, isouter=True)
            .join(KakaoPlace, Place.id == KakaoPlace.place_id, isouter=True)
            .group_by(Place.id)
        )
        query = query.order_by(desc("max_review_count") if order == "desc" else asc("max_review_count"))
    elif sort_by == "score":
        query = (
            db.query(
                Place,
                func.greatest(
                    func.coalesce(NaverPlace.score, 0),
                    func.coalesce(KakaoPlace.score, 0)
                ).label("max_score")
            )
            .join(NaverPlace, Place.id == NaverPlace.place_id, isouter=True)
            .join(KakaoPlace, Place.id == KakaoPlace.place_id, isouter=True)
            .group_by(Place.id)
        )
        query = query.order_by(desc("max_score") if order == "desc" else asc("max_score"))
    else:
        raise ValueError(f"Invalid sort_by value: {sort_by}")

    places = query.offset(offset).limit(limit).all()
    return [get_place_details(db, place if sort_by == "name" else place[0]) for place in places]


def get_places_by_score(
    db: Session, 
    order: Optional[str],
    offset: int, 
    limit: int,
) -> List[PlaceDetailsResponse]:
    query = query.order_by(desc(getattr(Place, sort_by))) if order == "desc" else query.order_by(asc(getattr(Place, sort_by)))
    places = query.offset(offset).limit(limit).all()

    return [get_place_details(db, place) for place in places]


def get_place_coordinate(db: Session, place_id: int) -> Optional[LatitudeLongitudeResponse]:
    coordinate = db.query(Place.pos_x, Place.pos_y).filter(Place.id == place_id).first()
    if coordinate:
        longitude, latitude = toLatLng(coordinate.pos_x, coordinate.pos_y)
        return LatitudeLongitudeResponse(latitude=latitude, longitude=longitude)
    return None


def get_place_details(db: Session, place: Place) -> Optional[PlaceDetailsResponse]:
    if not place:
        return None

    longitude, latitude = toLatLng(place.pos_x, place.pos_y)
    
    naver_info = get_naver_place_info(db, place.id)
    kakao_info = get_kakao_place_info(db, place.id)

    return PlaceDetailsResponse(
        basic_info=BasicPlaceInfoResponse(
            id=place.id,
            name=place.name,
            address=place.address,
            street_address=place.street_address,
            category=place.category.name,
            LatLng=LatitudeLongitudeResponse(latitude=latitude, longitude=longitude)
        ),
        naver_info=naver_info if naver_info else None,
        kakao_info=kakao_info if kakao_info else None
    )


def get_place_recommend(db: Session, model, tafp_df, user_id: int) -> List[PlaceDetailsResponse]:
    user = db.query(User).filter(User.id == user_id).first()

    user_info = [isWeekend(), getSeason(), 0 if user.sex == False else 1, user.age_group]
    user_cluster = model.predict([user_info])[0]

    recommended_places = tafp_df[model.labels_ == user_cluster]
    place_names = recommended_places.sort_values("pop", ascending=False)["name"].unique()[:10].tolist()

    return [
        place for place_name in place_names 
        if (place := get_place_by_name(db, place_name)) is not None
    ]
