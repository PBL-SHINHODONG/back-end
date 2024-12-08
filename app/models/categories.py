from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)

    places = relationship("Place", back_populates="category")
    naver_places = relationship("NaverPlace", back_populates="category")
    kakao_places = relationship("KakaoPlace", back_populates="category")
