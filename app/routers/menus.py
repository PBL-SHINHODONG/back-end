from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page, Params, paginate, add_pagination

from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.menus import MenuResponse
from app.crud import menus

router = APIRouter(
    prefix="/menus",
    tags=["menus"],
    responses={404: {"description": "Not found"}},
)
add_pagination(router)


@router.get("/{place_id}", response_model=Page[MenuResponse])
async def get_menu_by_place_id(
    place_id: int, 
    params: Params = Depends(), 
    db: Session = Depends(get_db)
):
    menu = menus.get_menu_by_place_id(db, place_id)
    if not menu:
        raise HTTPException(status_code=404, detail="menu not found")
    return paginate(menu, params)
