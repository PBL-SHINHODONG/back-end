from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class VisitedPlace(Base):
    __tablename__ = "visited_place"
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("place.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    visit_count = Column(Integer, default=1)
    
    user = relationship("User", back_populates="visited_places")
    place = relationship("Place", back_populates="visited_places")
