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
    PostcodeQueryParams,
)
from app.crud.postcodes import get_items, create, create_multiple, delete_postcode

# Set the base router
router = APIRouter(prefix="/" + URL_SEARCH)


@router.get("/", tags=["search"], response_model=list[PostcodeResponseSchema])
async def read_latlons(
    query_data: PostcodeQueryParams = Depends(), db: Session = Depends(create_session)
) -> list[PostcodeResponseSchema]:
    """Get the latitude and longitudes from a postcode.

    e.g. http://localhost:8000/search?postcode=example_name&min_lat=10.0&min_lon=100.0

    Can also break this up into a service and data manager layer for separation
    between crud and router.
    """
    try:
        return get_items(db, query_data)
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


@router.post("/add-multiple", tags=["search"])
async def create_multiple_items(
    items: list[PostcodeCreateSchema], db: Session = Depends(create_session)
):
    """Create multiple items in the DB by supplying a list of dictionaries defining
    the Postcode, latitudes and longitudes."""
    try:
        create_multiple(db, items)
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
