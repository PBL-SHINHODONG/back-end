from sqlalchemy import Column, Integer, String, Float, Boolean

from app.database import Base

class TafpDataset(Base):
    __tablename__ = "tafp_dataset"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    isWeekend = Column(Boolean, nullable=False)
    season = Column(Integer, nullable=False)
    sex = Column(Boolean, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    population = Column(Float, nullable=False)
