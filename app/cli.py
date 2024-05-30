"""Command-line interface definition for managing the database in the project from an
admin perspective.

Entries can be added, removed, or multi-added from the CLI.
"""

import argparse
import requests
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import Connection, create_engine
from app.models.postcodes import Postcodes
from app.const import LOCALHOST, URL_SEARCH

# ---------------------------------------------------------------------------- #
#  _____                            ____        _
# |  __ \                          / __ \      | |
# | |__) |_ _ _ __ ___  ___ _ __  | |  | |_ __ | |_ ___
# |  ___/ _` | '__/ __|/ _ \ '__| | |  | | '_ \| __/ __|
# | |  | (_| | |  \__ \  __/ |    | |__| | |_) | |_\__ \
# |_|   \__,_|_|  |___/\___|_|     \____/| .__/ \__|___/
#                                        | |
#                                        |_|
# ---------------------------------------------------------------------------- #

parser = argparse.ArgumentParser()
# ------------------------------- Boolean args ------------------------------- #
parser.add_argument(
    "--create",
    dest="create",
    help="option to create a new db entry",
    action="store_true",
)
parser.add_argument(
    "--get",
    dest="get",
    help="option to get a db entry",
    action="store_true",
)
parser.add_argument(
    "--delete",
    dest="delete",
    help="option to delete a db entry",
    action="store_true",
)
# ------------------------------ Key-value args ------------------------------ #
parser.add_argument(
    "--postcode",
    dest="postcode",
    help="full postcode for get or create",
    action="store",
)
parser.add_argument(
    "--district",
    dest="district",
    help="district postcode for get",
    action="store",
)
parser.add_argument(
    "--subarea",
    dest="subarea",
    help="subarea postcode for get",
    action="store",
)
parser.add_argument(
    "--min-lat",
    dest="min_lat",
    help="minimum latitude for get",
    action="store",
    type=float,
)
parser.add_argument(
    "--max-lat",
    dest="max_lat",
    help="maximum latitude for get",
    action="store",
    type=float,
)
parser.add_argument(
    "--min-lon",
    dest="min_lon",
    help="minimum lonitude for get",
    action="store",
    type=float,
)
parser.add_argument(
    "--max-lon",
    dest="max_lon",
    help="maximum lonitude for get",
    action="store",
    type=float,
)
parser.add_argument(
    "--lat",
    dest="lat",
    help="associated latitude for postcode",
    action="store",
    type=float,
)
parser.add_argument(
    "--lon",
    dest="lon",
    help="associated longitude for postcode",
    action="store",
    type=float,
)
# Parse arguments
args = parser.parse_args()

# ---------------------------------------------------------------------------- #
#   _____ _      _____   ______                _   _
#  / ____| |    |_   _| |  ____|              | | (_)
# | |    | |      | |   | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
# | |    | |      | |   |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |____| |____ _| |_  | |  | |_| | | | | (__| |_| | (_) | | | \__ \
#  \_____|______|_____| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
# ---------------------------------------------------------------------------- #


def create(args) -> None:
    # Create input json
    data = {"postcode": args.postcode, "lat": args.lat, "lon": args.lon}
    response = requests.post(
        f"{LOCALHOST}/{URL_SEARCH}/add",
        json=data,
        headers={"Content-Type": "application/json"},
    )
    print(response.content)


def delete(args) -> None:
    # Delete an item
    response = requests.delete(f"{LOCALHOST}/{URL_SEARCH}/{args.postcode}")
    print(response.content)


def get(args) -> None:
    data = {
        "full_postcode": args.postcode,
        "district_postcode": args.district,
        "subarea_postcode": args.subarea,
        "latitude": args.lat,
        "longitude": args.lon,
        "min_lat": args.min_lat,
        "max_lat": args.max_lat,
        "min_lon": args.min_lon,
        "max_lon": args.max_lon,
    }
    response = requests.get(
        f"{LOCALHOST}/{URL_SEARCH}/",
        json=data,
        headers={"Content-Type": "application/json"},
    )
    print(response.content)


def create_multiple() -> None:
    """Pass in a dictionary of lists, where each entry is a dictionary of the
    following:
        - Postcode
        - latitude
        - longitude

    Large-scale additions like this are not done through queries and are done by
    developer directly on db.
    """
    data = pd.read_csv("_cache/ukpostcodes.csv.zip", compression="zip")
    codes = data["postcode"].values
    district = data["postcode"].apply(lambda x: x.split(" ")[0]).values
    sub = data["postcode"].apply(lambda x: x.split(" ")[0][:2]).values
    lats = data["latitude"].values
    lons = data["longitude"].values

    engine = create_engine("sqlite:///data/postcodes.db")
    with Session(engine) as session:
        for chunk in range(0, len(codes), 1000):
            session.add_all(
                [
                    Postcodes(
                        **{
                            "full_postcode": codes[i],
                            "district_postcode": district[i],
                            "subarea_postcode": sub[i],
                            "latitude": lats[i],
                            "longitude": lons[i],
                        }
                    )
                    for i in range(chunk, min(chunk + 1000, len(codes)))
                ]
            )
            session.commit()
            print(chunk / len(codes) * 100)


# ---------------------------------------------------------------------------- #
#   _____ _      _____   _                 _
#  / ____| |    |_   _| | |               (_)
# | |    | |      | |   | |     ___   __ _ _  ___
# | |    | |      | |   | |    / _ \ / _` | |/ __|
# | |____| |____ _| |_  | |___| (_) | (_| | | (__
#  \_____|______|_____| |______\___/ \__, |_|\___|
#                                     __/ |
#                                    |___/
# ---------------------------------------------------------------------------- #

if args.create:
    # Create entry in db
    create(args)

if args.get:
    # Perform get request
    get(args)

if args.delete:
    delete(args)