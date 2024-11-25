from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page, Params, paginate, add_pagination

from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.search import SearchResponse
from app.crud import search

router = APIRouter(
    prefix="/search",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)
add_pagination(router)


@router.get("/{keyword}", response_model=Page[SearchResponse])
async def search_keyword(
    keyword: str, 
    params: Params = Depends(),
    db: Session = Depends(get_db)
):
    result = search.search_keyword(db, keyword)
    if not result:
        raise HTTPException(status_code=404, detail="Search not found")
    return paginate(result, params)
