from pydantic import BaseModel

from typing import Optional

class PlaceResponse(BaseModel):
    name: str
    category: str
    crawled_category: str
    pos_x: float
    pos_y: float
    score: Optional[float]
    review_count: int
    address: Optional[str]
    street_address: str

class PlaceCordinateResponse(BaseModel):
    pos_x: float
    pos_y: float
