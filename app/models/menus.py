from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Menu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("place.id"), nullable=False)
    menu = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)

    place = relationship("Place", back_populates="menus")
