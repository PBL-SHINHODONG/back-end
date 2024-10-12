from fastapi import APIRouter

from fastapi_pagination import add_pagination

from schemas.users import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

add_pagination(router)

@router.get("/{user_id}")
async def get_user(user_id: str) -> UserResponse:
    return {"username": "fakecurrentuser"}


