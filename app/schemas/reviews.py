from pydantic import BaseModel
from typing import Optional

class ReviewsCreateRequest(BaseModel):
    place_id: int
    user_id: Optional[int]
    comment: str
    score: Optional[float]


class ReviewResponse(BaseModel):
    id: int
    place_id: int
    user_id: Optional[int]
    comment: str
    
    class Config:
        from_attributes = True
