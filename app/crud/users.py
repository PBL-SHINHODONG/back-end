from typing import Optional

from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.users import UserResponse, UserCreateRequest, UserLoginRequest

def get_user_by_id(session: Session, user_id: int) -> Optional[UserResponse]:
    return session.query(User).filter(User.id == user_id).first()


def login(session: Session, user: UserLoginRequest) -> Optional[UserResponse]:
    user = session.query(User).filter(User.email == user.email).first()
    if user and user.password == user.password:
        return user
    return None 


def register(session: Session, user: UserCreateRequest) -> Optional[UserResponse]:
    if session.query(User).filter(User.email == user.email).first():
        return None 

    new_user = User(
        email=user.email,
        password=user.password,
        sex=user.sex,
        age_group=user.age_group,
        preferred_food=user.preferred_food,
        preferred_activity=user.preferred_activity,
        budget_range=user.budget_range,
        preferred_atmosphere=user.preferred_atmosphere,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def delete_user(session: Session, user_id: int) -> bool:
    user = session.query(User).filter(User.id == user_id).first()
    
    if user:
        session.delete(user)
        session.commit()
        return True
    return False
