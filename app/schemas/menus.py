from pydantic import BaseModel

class MenuResponse(BaseModel):
    place_id: int
    menu: str
    price: int
