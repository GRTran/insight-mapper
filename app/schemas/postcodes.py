"""Schema for model response containing lat and lon data.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PostcodeBase(BaseModel):
    full_postcode: Optional[str] = Field(None, example="A full postcode: YO1 2GH")
    district_postcode: Optional[str] = Field(None, example="A district postcode: KT")
    subarea_postcode: Optional[str] = Field(None, example="A more local postcode: KT6")
    latitude: Optional[float] = Field(None, example="The latitude")
    longitude: Optional[float] = Field(None, example="The longitude")


class PostcodeQueryParams(PostcodeBase):
    min_lat: Optional[float] = Field(None)
    max_lat: Optional[float] = Field(None)
    min_lon: Optional[float] = Field(None)
    max_lon: Optional[float] = Field(None)


class PostcodeCreateSchema(BaseModel):
    """Creates an item in postcodes db"""

    postcode: str
    lat: float
    lon: float


class PostcodeResponseSchema(PostcodeBase):
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


class LandRegistrySchema(LatLonSummarySchema):
    """All data associated with"""

    sold_prices: list[float] 
    dates: list[datetime] = Field(None)
