from fastapi import APIRouter, HTTPException
from fastapi_pagination import add_pagination

from app.database import SessionLocal
from app.schemas.users import UserResponse, UserCreateRequest, UserLoginRequest
from app.crud import users

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

session = SessionLocal()
add_pagination(router)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = users.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException( status_code=401, detail="User not found")
    return user


@router.post("/login", response_model=UserResponse)
async def login(user: UserLoginRequest):
    user = users.login(session, user)
    if not user:
        raise HTTPException( status_code=401, detail="Invalid email or password")
    return user


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreateRequest):
    user = users.register(session, user)
    if not user:
        raise HTTPException( status_code=401, detail="Invalid email or password")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    success = users.delete_user(session, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
