from typing import Optional

from sqlalchemy.orm import Session

from app.schemas.menus import MenuResponse
from app.models.places import Place
from app.models.menus import Menu

def get_menu_by_place_id(db: Session, place_id: int) -> Optional[MenuResponse]:
    return db.query(Menu).filter(Menu.place_id == place_id).all()
