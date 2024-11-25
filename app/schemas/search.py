from pydantic import BaseModel
from typing import Optional

class SearchResponse(BaseModel):
    place_id: Optional[int]
    place_name: Optional[str]
    menu_name: Optional[str]
