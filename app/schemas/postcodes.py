"""Schema for model response containing lat and lon data.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GeometricSchema(BaseModel):
    min_lat: Optional[float] = Field(None)
    max_lat: Optional[float] = Field(None)
    min_lon: Optional[float] = Field(None)
    max_lon: Optional[float] = Field(None)


class PostcodeSchema(GeometricSchema):
    full_postcode: Optional[str] = Field(None, example="A full postcode: YO1 2GH")
    district_postcode: Optional[str] = Field(None, example="A district postcode: KT")
    subarea_postcode: Optional[str] = Field(None, example="A more local postcode: KT6")
    latitude: Optional[float] = Field(None, example="The latitude")
    longitude: Optional[float] = Field(None, example="The longitude")


class PostcodeCreateSchema(BaseModel):
    """Creates an item in postcodes db"""

    postcode: str
    lat: float
    lon: float


class PostcodeResponseSchema(PostcodeSchema):
    """Response for the create/update"""

    id: int

    class Config:
        orm_mode = True


class LatLonBoundsSchema(BaseModel):
    """The bounds of a square."""
    bottom_left: list[float] 
    bottom_right: list[float] 
    upper_right: list[float] 
    upper_left: list[float]


class LatLonSummarySchema(LatLonBoundsSchema):
    """Summary of number of postcodes falling in bounds."""
    #:n_postcodes: defines the number of postcodes falling within this space.
    n_postcodes: Optional[int] = Field(0)


class PricesSchema(LatLonBoundsSchema):
    """All data associated with"""

    two_yr_avg: float | None
    five_yr_avg: float | None
