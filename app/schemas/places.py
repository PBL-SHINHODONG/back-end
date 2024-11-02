from pydantic import BaseModel
from typing import Optional

class LatitudeLongitudeResponse(BaseModel):
    latitude: float
    longitude: float


class BasicPlaceInfoResponse(BaseModel):
    name: str
    address: Optional[str]
    street_address: str
    category: str
    LatLng: LatitudeLongitudeResponse


class NaverPlaceInfoResponse(BaseModel):
    street_address: str 
    category: str 
    score: Optional[float]
    review_count: int


class KakaoPlaceInfoResponse(BaseModel):
    street_address: str 
    category: str
    score: Optional[float]
    review_count: int


class PlaceDetailsResponse(BaseModel):
    basic_info: BasicPlaceInfoResponse
    naver_info: Optional[NaverPlaceInfoResponse] = None
    kakao_info: Optional[KakaoPlaceInfoResponse] = None
