from fastapi import Request, APIRouter, HTTPException, Depends
from fastapi_pagination import Page, Params, paginate, add_pagination

from typing import List, Optional, Union

from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.places import (
    PlaceDetailsResponse, 
    LatitudeLongitudeResponse,
    NaverPlaceInfoResponse,
    KakaoPlaceInfoResponse
)
from app.crud import places
from app.schemas.users import UserPresentLocation

router = APIRouter(
    prefix="/places",
    tags=["places"],
    responses={404: {"description": "Not found"}},
)
add_pagination(router)

@router.get("/{place_id}", response_model=PlaceDetailsResponse)
async def get_place_by_id(place_id: int, db: Session = Depends(get_db)):
    place = places.get_place_by_id(db, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="place not found")
    return place


@router.get("/{place_id}/naver", response_model=NaverPlaceInfoResponse)
async def get_naver_place(place_id: int, db: Session = Depends(get_db)):
    naver_info = places.get_naver_place_info(db, place_id)
    if not naver_info:
        raise HTTPException(status_code=404, detail="Naver place info not found")
    return naver_info


@router.get("/{place_id}/kakao", response_model=KakaoPlaceInfoResponse)
async def get_kakao_place(place_id: int, db: Session = Depends(get_db)):
    kakao_info = places.get_kakao_place_info(db, place_id)
    if not kakao_info:
        raise HTTPException(status_code=404, detail="Kakao place info not found")
    return kakao_info


@router.get("/name/{place_name}", response_model=PlaceDetailsResponse)
async def get_place_by_name(place_name: str, db: Session = Depends(get_db)):
    place = places.get_place_by_name(db, place_name)
    if not place:
        raise HTTPException(status_code=404, detail="place not found")
    return place


@router.get("/", response_model=Page[PlaceDetailsResponse])
async def get_places(
    sort_by: Union[str, None] = None,
    order: Optional[str] = "desc",
    page_size: Optional[int] = 10,
    params: Params = Depends(),
    db: Session = Depends(get_db)
):
    params.size = limit = min(page_size, 50)
    offset = (params.page - 1) * params.size

    place_list = places.get_places(db, sort_by, order, offset, limit)
    if not place_list:
        raise HTTPException(status_code=404, detail="places not found")
    return paginate(place_list, params)


@router.get("/{place_id}/coordinates", response_model=LatitudeLongitudeResponse)
async def get_place_coordinate(place_id: int, db: Session = Depends(get_db)):
    coordinate = places.get_place_coordinate(db, place_id)
    if not coordinate:
        raise HTTPException(status_code=404, detail="coordinate not found")
    return coordinate


@router.get("/{user_id}/recommend", response_model=Page[PlaceDetailsResponse])
async def get_place_recommend(
    user_id: int, 
    request: Request, 
    params: Params = Depends(), 
    db: Session = Depends(get_db)
):
    params.size = 10
    model = request.app.state.model
    tafp_df = request.app.state.tafp_df
    place_list = places.get_place_recommend(db, model, tafp_df, user_id)
    if not place_list:
        raise HTTPException(status_code=404, detail="places not found")
    return paginate(place_list, params)


@router.get("/content/{category}", response_model=List[PlaceDetailsResponse])
async def get_content_based_recommend(user: UserPresentLocation, category : str, db: Session = Depends(get_db)):
    place_list = places.get_content_based_recommend(db, user, category)
    if not place_list:
        raise HTTPException(status_code=404, detail="places not found")
    return place_list
