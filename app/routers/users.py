from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import add_pagination

from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.users import UserResponse, UserCreateRequest, UserLoginRequest
from app.crud import users

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)
add_pagination(router)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = users.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/login", response_model=UserResponse)
async def login(user: UserLoginRequest, db: Session = Depends(get_db)):
    user = users.login(db, user)
    if not user:
        raise HTTPException( status_code=401, detail="Invalid email or password")
    return user


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreateRequest, db: Session = Depends(get_db)):
    user = users.register(db, user)
    if not user:
        raise HTTPException( status_code=401, detail="Invalid email or password")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = users.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
