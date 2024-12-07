from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    email: str
    password: str
    sex: bool
    age_group: int
    preferred_food: str
    preferred_activity: str
    budget_range: str
    preferred_atmosphere: str

class UserResponse(BaseModel):
    id: int
    email: str
    sex: bool
    age_group: int
    preferred_food: str
    preferred_activity: str
    budget_range: str
    preferred_atmosphere: str

    class Config:
        from_attributes = True

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserPresentLocation(BaseModel):
    id: int
    latitude: float
    longitude: float