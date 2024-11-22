from pydantic import BaseModel

class VisitedPlaceResponse(BaseModel):
    place_id: int
    user_id: int
    visit_count: int

class VisitedPlaceCreateRequest(BaseModel):
    place_id: int
    user_id: int
