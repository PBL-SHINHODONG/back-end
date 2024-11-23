from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True)
    password = Column(String(255), unique=True, nullable=False)
    sex = Column(Boolean, unique=True, nullable=False)
    age_group = Column(Integer, nullable=False)
    preferred_food = Column(String(255), nullable=False)
    preferred_activity = Column(String(255), nullable=False)
    budget_range = Column(String(255), nullable=False)
    preferred_atmosphere = Column(String(255), nullable=False)

    visited_places = relationship("VisitedPlace", back_populates="user")
    reviews = relationship("Review", back_populates="user")
