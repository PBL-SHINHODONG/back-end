from typing import List, Optional, Union

from sqlalchemy import desc, asc, literal, or_
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.schemas.places import (
    BasicPlaceInfoResponse,
    PlaceDetailsResponse, 
    LatitudeLongitudeResponse,
    NaverPlaceInfoResponse,
    KakaoPlaceInfoResponse
)
from app.models.places import Place, NaverPlace, KakaoPlace
from app.models.users import User
from app.models.visitedplaces import VisitedPlace
from app.dependencies import getSeason, isWeekend, getCategory, haversine_query
from app.schemas.users import UserPresentLocation

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


def get_place_coordinate(db: Session, place_id: int) -> Optional[LatitudeLongitudeResponse]:
    coordinate = db.query(Place.pos_x, Place.pos_y).filter(Place.id == place_id).first()
    if coordinate:
        latitude, longitude = coordinate.pos_x, coordinate.pos_y
        return LatitudeLongitudeResponse(latitude=latitude, longitude=longitude)
    return None


def get_place_details(db: Session, place: Place) -> Optional[PlaceDetailsResponse]:
    if not place:
        return None

    latitude, longitude = place.pos_x, place.pos_y
    
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

def places_filtering(db, user, query):
    # 1. 방문한 장소 제외
    visited_places_subquery = (
        db.query(VisitedPlace.place_id)
        .filter(VisitedPlace.user_id == user.id)
        .subquery()
    )
    query = query.filter(~Place.id.in_(visited_places_subquery))

    # 2. 거리 필터링
    user_lat, user_lon = user.latitude, user.longitude

    # 2.1 거리 계산 및 필터링(10km 이내)  
    query = query.filter(
        haversine_query(
            literal(user_lat),
            literal(user_lon),
            Place.pos_x,
            Place.pos_y
        ) < 10
    )

    # 3. 평균 계산 로직 (None 값을 무시)
    avg_score = case(
        (NaverPlace.score.isnot(None) & KakaoPlace.score.isnot(None), (NaverPlace.score + KakaoPlace.score) / 2),
        (NaverPlace.score.isnot(None), NaverPlace.score),
        (KakaoPlace.score.isnot(None), KakaoPlace.score),
        else_=None
    )

    avg_review_count = case(
        (NaverPlace.review_count.isnot(None) & KakaoPlace.review_count.isnot(None), (NaverPlace.review_count + KakaoPlace.review_count) / 2),
        (NaverPlace.review_count.isnot(None), NaverPlace.review_count),
        (KakaoPlace.review_count.isnot(None), KakaoPlace.review_count),
        else_=None
    )

    query = query.filter(avg_score.isnot(None))

    # 3. 평균 점수 및 리뷰 수 기준 정렬
    query = query.order_by(avg_score.desc(), avg_review_count.desc())

    # 4. 상위 10개만 반환 및 ID 추출
    place_ids = query.with_entities(Place.id).limit(10).all()

    return [place_id[0] for place_id in place_ids]


def filter_by_category(query, category):
    subcategory_ids = getCategory(category)
    if subcategory_ids:
        query = query.filter(
            or_(
                *(NaverPlace.subcategory_id == id for id in subcategory_ids),
                *(KakaoPlace.subcategory_id == id for id in subcategory_ids),
            )
        )
    return query

def get_content_based_recommend(db: Session, user : UserPresentLocation, category: str) -> List[PlaceDetailsResponse]:
    # 쿼리 작성
    query = db.query(
        Place.id,
        Place.pos_x,
        Place.pos_y,
        NaverPlace.subcategory_id,
        NaverPlace.score,
        NaverPlace.review_count,
        KakaoPlace.subcategory_id,
        KakaoPlace.score,
        KakaoPlace.review_count
    ).outerjoin(NaverPlace, Place.id == NaverPlace.place_id)\
    .outerjoin(KakaoPlace, Place.id == KakaoPlace.place_id)
    query = filter_by_category(query, category)
    place_id_list = places_filtering(db, user, query)
    return [
        place for id in place_id_list
        if (place := get_place_by_id(db, id)) is not None
    ]