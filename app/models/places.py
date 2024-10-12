from sqlalchemy import Column, Integer, String, Float

from app.database import Base

class Place(Base):
    __tablename__ = "place"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    category = Column(String(255), index=True, nullable=False)
    crawled_category = Column(String(255), index=True, nullable=False)
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    score = Column(Float)
    review_count = Column(Integer, nullable=False)
    address = Column(String(255))
    street_address = Column(String(255))
