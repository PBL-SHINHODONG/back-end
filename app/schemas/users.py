from pydantic import BaseModel

class UserResponse(BaseModel):
    email: str
    age: int
    sex: bool
    latitude: float
    longitutde: float
