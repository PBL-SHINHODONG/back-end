from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Review(Base):
    __tablename__ = "review"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    place_id = Column(Integer, ForeignKey("place.id"), nullable=False)
    comment = Column(String(255), nullable=False)
    score = Column(Float)

    user = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews")
