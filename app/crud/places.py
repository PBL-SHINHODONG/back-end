import numpy as np

from typing import List, Optional

from sqlalchemy import desc, asc, literal, or_
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.schemas.places import (
    BasicPlaceInfoResponse,
    PlaceDetailsResponse, 
    LatitudeLongitudeResponse,
    NaverPlaceInfoResponse,
    KakaoPlaceInfoResponse,
    ContentBasedRecommedRequest,
    CollaborativeBasedRecommendRequest
)
from app.models.places import Place, NaverPlace, KakaoPlace
from app.models.users import User
from app.models.visitedplaces import VisitedPlace
from app.dependencies import getSeason, isWeekend, getCategoryCode, getHaversine, getCategoryName


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


def get_cluster_based_recommend(
    db: Session, 
    model, 
    tafp_df, 
    user_id: int
) -> List[PlaceDetailsResponse]:
    user = db.query(User).filter(User.id == user_id).first()

    user_info = [isWeekend(), getSeason(), 0 if user.sex == False else 1, user.age_group]
    user_cluster = model.predict([user_info])[0]

    recommended_places = tafp_df[model.labels_ == user_cluster]
    place_names = recommended_places.sort_values("pop", ascending=False)["name"].unique()[:10].tolist()

    return [
        place for place_name in place_names 
        if (place := get_place_by_name(db, place_name)) is not None
    ]


def get_content_based_recommend(
    db: Session, 
    category: str,
    payload: ContentBasedRecommedRequest
) -> List[PlaceDetailsResponse]:
    visited_places_ids = db.query(VisitedPlace.place_id).filter(VisitedPlace.user_id == payload.user_id).subquery()

    final_subcategories = (
        db.query(NaverPlace.subcategory_id)
        .filter(NaverPlace.place_id.in_(visited_places_ids))
        .union(
            db.query(KakaoPlace.subcategory_id)
            .filter(KakaoPlace.place_id.in_(visited_places_ids))
        )
        .all()
    )

    final_subcategories = [row[0] for row in final_subcategories]

    all_place_ids = db.query(Place.id).all()


    final_filtered_ids = []
    unique_subcategories = list(set(final_subcategories))

    subcategory_ratio = {
        subcategory: final_subcategories.count(subcategory) / len(final_subcategories)
        for subcategory in unique_subcategories
    }

    for subcategory_id, ratio in subcategory_ratio.items():
        category_name = getCategoryName(subcategory_id)
        category_filtered_ids = filter_by_category(db, [id[0] for id in all_place_ids], category_name)
        filtered_distance_ids = filter_by_dist(db, category_filtered_ids, payload, False)
        num_to_select = round(ratio * payload.top_n)

        final_filtered_ids.extend(filtered_distance_ids[:num_to_select])

    if not final_filtered_ids:
        final_filtered_ids = filter_by_dist(db, [id[0] for id in all_place_ids], payload, True)[:payload.top_n]

    return [
        place for id in final_filtered_ids
        if (place := get_place_by_id(db, id)) is not None
    ]

def get_collaborative_based_recommend(
    db: Session,
    model,
    category: str,
    payload : CollaborativeBasedRecommendRequest
) -> List[PlaceDetailsResponse]:

    place_size = 23443

    visited_places = (
        db.query(VisitedPlace.place_id, VisitedPlace.visit_count)
        .filter(VisitedPlace.user_id == payload.user_id)
        .all()
    )
    visited_places_dict = {place_id: visit_count for place_id, visit_count in visited_places}

    all_places = np.arange(1, place_size + 1)
    user_ids = np.full(len(all_places), payload.user_id)
    visit_count = np.array([
        visited_places_dict.get(place_id, 0)
        for place_id in all_places
    ])
    
    predicted_scores = model.predict([user_ids, all_places, visit_count])

    place_id_list = all_places[np.argsort(predicted_scores.flatten())[::-1][:20]]

    return [
        place for id in place_id_list
        if (place := get_place_by_id(db, id)) is not None
    ]


def filter_by_dist(db: Session, place_ids: List[int], payload: ContentBasedRecommedRequest, empty) -> List[int]:
    user_lat, user_lon = payload.latitude, payload.longitude

    filtered_ids = (
        db.query(Place.id)
        .outerjoin(NaverPlace, NaverPlace.place_id == Place.id)
        .outerjoin(KakaoPlace, KakaoPlace.place_id == Place.id)
        .filter(
            Place.id.in_(place_ids),
            ~Place.id.in_(
                db.query(VisitedPlace.place_id).filter(VisitedPlace.user_id == payload.user_id)
            ),
            *([] if empty else [getHaversine(literal(user_lat), literal(user_lon), Place.pos_x, Place.pos_y) < 10]),
            case(
                (
                    NaverPlace.score.isnot(None) & KakaoPlace.score.isnot(None),
                    (NaverPlace.score + KakaoPlace.score) / 2
                ),
                (NaverPlace.score.isnot(None), NaverPlace.score),
                (KakaoPlace.score.isnot(None), KakaoPlace.score),
                else_=None
            ).isnot(None)
        )
        .order_by(
            case(
                (
                    NaverPlace.score.isnot(None) & KakaoPlace.score.isnot(None),
                    (NaverPlace.score + KakaoPlace.score) / 2
                ),
                (NaverPlace.score.isnot(None), NaverPlace.score),
                (KakaoPlace.score.isnot(None), KakaoPlace.score),
                else_=None
            ).desc(),
            case(
                (
                    NaverPlace.review_count.isnot(None) & KakaoPlace.review_count.isnot(None),
                    (NaverPlace.review_count + KakaoPlace.review_count) / 2
                ),
                (NaverPlace.review_count.isnot(None), NaverPlace.review_count),
                (KakaoPlace.review_count.isnot(None), KakaoPlace.review_count),
                else_=None
            ).desc()
        )
        .all()
    )

    return [id[0] for id in filtered_ids]

def filter_by_category(db: Session, place_ids: List[int], category: str) -> List[int]:
    subcategory_ids = getCategoryCode(category)
    if not subcategory_ids:
        return []

    filtered_ids = (
        db.query(Place.id)
        .outerjoin(NaverPlace, NaverPlace.place_id == Place.id)
        .outerjoin(KakaoPlace, KakaoPlace.place_id == Place.id)
        .filter(
            Place.id.in_(place_ids),
            or_(
                NaverPlace.subcategory_id.in_(subcategory_ids),
                KakaoPlace.subcategory_id.in_(subcategory_ids),
            )
        )
        .all()
    )
    return [id[0] for id in filtered_ids]
