from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Place(Base):
    __tablename__ = "place"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    address = Column(String(255))
    street_address = Column(String(255))
    category = Column(String(255), index=True, nullable=False)
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)

    visited_places = relationship("VisitedPlace", back_populates="place")
    menus = relationship("Menu", back_populates="place")
    reviews = relationship("Review", back_populates="place")

    
class NaverPlace(Base):
    __tablename__ = "n_place"
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("place.id"))
    street_address = Column(String(255))
    category = Column(String(255), index=True)
    score = Column(Float)
    review_count = Column(Integer, nullable=False)


class KakaoPlace(Base):
    __tablename__ = "k_place"
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("place.id"))
    street_address = Column(String(255))
    category = Column(String(255), index=True)
    score = Column(Float)
    review_count = Column(Integer, nullable=False)
    
