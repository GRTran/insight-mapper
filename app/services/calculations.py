"""Service layer calculations"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.schemas.postcodes import LatLonBoundsSchema, LatLonSummarySchema
from app.crud.postcodes import get_items_from_latlon


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

async def npostcodes(subsquares: list[LatLonBoundsSchema]) -> LatLonSummarySchema:
    """Takes in the sub-squares and queries db, summarising results.
    """

    # Execute the thread pool within the async event loop running synchronous crud operation
    async def _single_query(square):
        return await asyncio.get_event_loop().run_in_executor(
            None,
            get_items_from_latlon, square
        )
    
    result = await asyncio.gather(*[_single_query(square) for square in subsquares])
    # Summarise result