"""Other routers, rename file

Serves at the UI interaction layer.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import create_session
from app.const import URL_SEARCH
from app.schemas.postcodes import (
    PostcodeCreateSchema,
    PostcodeResponseSchema,
    PostcodeSchema,
    GeometricSchema,
    PricesSchema,
    LatLonSummarySchema,
    LatLonBoundsSchema,
)
from app.crud.postcodes import create, delete_postcode
from app.services import calculations, landregistry

# Set the base router
router = APIRouter(prefix="/" + URL_SEARCH)

@router.get("/average_prices", tags=["search"], response_model=list[PricesSchema])
async def avg_prices(query_data: GeometricSchema = Depends(), db: Session = Depends(create_session)
) -> list[PricesSchema]:
    """Query the external historical house price service."""
    try:
        # Separate the latitude and longitude by size
        return await landregistry.price_data(query_data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/npostcodes", tags=["search"], response_model=list[LatLonSummarySchema])
async def npostcodes(
    query_data: GeometricSchema = Depends(), db: Session = Depends(create_session)
) -> list[LatLonSummarySchema]:
    """Searches based purely on a maximum and minimum latitude/longitude."""
    try:
        # Separate the latitude and longitude by size
        return await calculations.npostcodes(query_data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/subsquares", tags=["search"], response_model=list[LatLonBoundsSchema])
async def subsquares(
    query_data: GeometricSchema = Depends(), db: Session = Depends(create_session)
) -> list[LatLonBoundsSchema]:
    """Returns equidistant subsquares from single square.
    """
    try:
        # Separate the latitude and longitude by size
        lats = (query_data.min_lat, query_data.max_lat)
        lons = (query_data.min_lon, query_data.max_lon)
        sub_squares = await calculations.separate_by_size(lats, lons)
        return sub_squares
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/add", tags=["search"], response_model=PostcodeResponseSchema)
async def create_latlons(
    item: PostcodeCreateSchema, db: Session = Depends(create_session)
):
    """Create an item in the data base from a postcode, latitude and longitude."""
    try:
        answer = create(db, item)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{postcode}", tags=["search"], status_code=204)
async def delete_item(postcode: str, db: Session = Depends(create_session)):
    """Delete an entry in the db if it is present."""
    try:
        delete_postcode(db, postcode)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
