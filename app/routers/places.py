from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi_pagination import Page, Params, paginate, add_pagination

from typing import Optional, Union

from app.database import SessionLocal
from app.schemas.places import PlaceResponse, PlaceCordinateResponse
from app.crud import places

router = APIRouter(
    prefix="/places",
    tags=["places"],
    responses={404: {"description": "Not found"}},
)

session = SessionLocal()
add_pagination(router)


@router.get("/{place_id}", response_model=PlaceResponse)
async def get_place_by_id(place_id: int):
    place = places.get_place_by_id(session, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="place not found")
    return place


@router.get("/{place_name}", response_model=PlaceResponse)
async def get_place_by_name(place_name: str):
    place = places.get_place_by_name(session, place_name)
    if not place:
        raise HTTPException(status_code=404, detail="place not found")
    return place


@router.get("/", response_model=Page[PlaceResponse])
async def get_places(
    sort_by: Union[str, None] = None,
    order: Optional[str] = "desc",
    page_size: Optional[int] = 10,
    params: Params = Depends(),
):
    params.size = page_size
    place_list = places.get_places(session, sort_by, order)
    if not place_list:
        raise HTTPException(status_code=404, detail="places not found")
    return paginate(place_list, params)


@router.get("/{place_id}/coordinates", response_model=PlaceCordinateResponse)
async def get_place_coordinate(place_id: int):
    coordinate = places.get_place_coordinate(session, place_id)
    if not coordinate:
        raise HTTPException(status_code=404, detail="coordinate not found")
    return coordinate


@router.get("/recommend", response_model=Page[PlaceResponse])
async def get_place_recommend():
    place_list = places.get_place_recommend(session)
    if not place_list:
        raise HTTPException(status_code=404, detail="places not found")
    return place_list

