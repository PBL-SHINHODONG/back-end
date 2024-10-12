from sqlalchemy import Column, Integer, String, Float

from database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitutde = Column(Float, nullable=False)
