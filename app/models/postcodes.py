"""Base SQLAlchemy models"""

from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base


class Postcodes(Base):
    __tablename__ = "postcodes"

    full_postcode = Column(String(8), index=True, nullable=False, unique=True)
    district_postcode = Column(String(2), index=True)
    subarea_postcode = Column(String(4), index=True)
    latitude = Column(Float(precision=6), nullable=False)
    longitude = Column(Float(precision=6), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
