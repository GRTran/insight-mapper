"""Acts as an interface between the schema and the db by modularising and separating the
responsibilities.

Create, Reuse, Update, Delete operations for the postcodes db.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.schemas.postcodes import (
    PostcodeCreateSchema,
    PostcodeResponseSchema,
    PostcodeQueryParams,
)
from app.models.postcodes import Postcodes


def get_items(
    db: Session, query_data: PostcodeQueryParams
) -> list[PostcodeResponseSchema]:
    """Filter the postcodes db depending on input arguments supplied."""
    q = db.query(Postcodes)
    if query_data.full_postcode:
        q = q.filter(Postcodes.full_postcode == query_data.full_postcode)
    if query_data.district_postcode:
        q = q.filter(Postcodes.district_postcode == query_data.district_postcode)
    if query_data.subarea_postcode:
        q = q.filter(Postcodes.subarea_postcode == query_data.subarea_postcode)
    if query_data.latitude:
        q = q.filter(Postcodes.latitude == query_data.latitude)
    if query_data.longitude:
        q = q.filter(Postcodes.longitude == query_data.longitude)
    if query_data.min_lat:
        q = q.filter(Postcodes.latitude >= query_data.min_lat)
    if query_data.max_lat:
        q = q.filter(Postcodes.latitude <= query_data.max_lat)
    if query_data.min_lon:
        q = q.filter(Postcodes.longitude >= query_data.min_lon)
    if query_data.max_lon:
        q = q.filter(Postcodes.longitude <= query_data.max_lon)
    result = db.execute(q)
    return result.scalars().all()


def create(db: Session, item: PostcodeCreateSchema) -> Postcodes:
    # separate postcode at the space
    elems = item.postcode.split(sep=" ")
    subdistrict = elems[0]
    district = elems[0][:2]

    db_item = Postcodes(
        full_postcode=item.postcode,
        district_postcode=district,
        subarea_postcode=subdistrict,
        latitude=item.lat,
        longitude=item.lon,
    )
    db.add(db_item)
    db.commit()
    return db_item


def delete_postcode(db: Session, postcode: str):
    result = db.execute(select(Postcodes).filter(Postcodes.full_postcode == postcode))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
