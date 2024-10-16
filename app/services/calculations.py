"""Service layer calculations"""
import asyncio
import pandas as pd
from sqlalchemy.orm import Session
from app.schemas.postcodes import LatLonBoundsSchema, LatLonSummarySchema, GeometricSchema
from app.crud.postcodes import get_frame_from_latlon


async def separate_by_size(
    lats: tuple, lons: tuple, nbins: int = 10
) -> list[LatLonBoundsSchema]:
    """Given maximum and minimum latitude and longitude, separate the square into
    10x10 sub-squares. This will then be used for data aggregation.

    The resulting square is defined starting at the bottom left, moving anti-clockwise.

       (4)           (3)
        .-------------.
        |             |
        |             | lon_spacing
        |             |
        |             |
        .-------------.
       (1)           (2)
          lat_spacing

    Args:
        lats (tuple): Maximum and minimum latitudes.
        lons (tuple): Maximum and minimum longitudes.

    Returns:
        list[tuple]: Maximum and minimum latitude and longitudes
    """
    lon_spacing = (max(lons) - min(lons)) / nbins
    lat_spacing = (max(lats) - min(lats)) / nbins

    subsquares = list()

    # Reference point always at the bottom left of the sub-square and create subsquares
    clon = min(lons)
    for _ in range(1, nbins + 1):
        clat = min(lats)
        for _ in range(1, nbins + 1):
            coordinates = LatLonBoundsSchema(
                bottom_left=[clat, clon],
                bottom_right=[clat + lat_spacing, clon],
                upper_right=[clat + lat_spacing, clon + lon_spacing],
                upper_left=[clat, clon + lon_spacing],
            )
            subsquares += [coordinates]
            clat += lat_spacing
        clon += lon_spacing
    return subsquares

async def npostcodes(bounds: GeometricSchema, db: Session) -> LatLonSummarySchema:
    """Takes in the maximum and minimum latitude and longitude and separates it into 
    100 sub-squares, also calculating the total number of postcodes falling in the
    sub-squares.

    Separates the results by size
    """
    # Get a dataframe of all of the db entries
    df = get_frame_from_latlon(db, bounds)

    # Filter based on subsquares
    lats = (bounds.min_lat, bounds.max_lat)
    lons = (bounds.min_lon, bounds.max_lon)
    sub_squares = await separate_by_size(lats, lons)

    # Create summary schema for each subsquare
    res = []
    for square in sub_squares:
        min_lat = square.bottom_left[0]
        max_lat = square.bottom_right[0]
        min_lon = square.bottom_left[1]
        max_lon = square.upper_left[1]
        mask = (
            (df["latitude"] >= min_lat)
            & (df["latitude"] < max_lat)
            & (df["longitude"] >= min_lon)
            & (df["longitude"] < max_lon)
        )
        res += [LatLonSummarySchema(**square.model_dump(), n_postcodes=len(df[mask]))]

    return res
