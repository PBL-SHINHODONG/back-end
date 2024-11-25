from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.schemas.search import SearchResponse
from app.models.places import Place
from app.models.menus import Menu


def search_keyword(db: Session, keyword: str) -> List[SearchResponse]:
    results = db.query(Place.id, Place.name, Menu.menu) \
        .join(Menu, Place.id == Menu.place_id) \
        .filter(or_(
            Place.name.like(f'%{keyword}%'),
            Menu.menu.like(f'%{keyword}%')
        )) \
        .all()

    return [SearchResponse(
        place_id=result[0],
        place_name=result[1],
        menu_name=result[2]
    ) for result in results]
