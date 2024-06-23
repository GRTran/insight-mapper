"""Get the query working so that we can look at historical house price sale data over a region
"""

import io
from typing import Iterable
from enum import Enum
from SPARQLWrapper import SPARQLWrapper, CSV
import pandas as pd
import matplotlib.pyplot as plt

from app.schemas.postcodes import (
    PostcodeResponseSchema,
    LandRegistrySchema,
)


class LocationCriteria(str, Enum):
    """
    Possible search criteria.
    street: str, town: str, county: str, postcode: str
    """

    PAON = "housenum"
    STREET = "street"
    TOWN = "town"
    COUNTY = "county"
    POSTCODE = "postcode"


class UKHPIQueryParams(str, Enum):
    """Names of entries for House Price Index (HPI) queries."""

    VOLUME = "salesVolume"
    VOLUMECASH = "salesVolumeCash"
    VOLUMEMORTGAGE = "salesVolumeMortgage"


class UKPPIQueryParams(str, Enum):
    """Information related to price paid information (PPI) for properties."""

    PROPERTYADDRESS = "propertyAddress"
    AMOUNT = "pricePaid"
    DATE = "transactionDate"
    PROPERTYTYPE = "propertyType"
    ESTATETYPE = "estateType"
    CATEGORY = "transactionCategory/skos:prefLabel"
    NEWBUILD = "newBuild"


class AddressQueryParams(str, Enum):
    HOUSENUM = "paon"
    FLATNUM = "saon"
    STREET = "street"
    TOWN = "town"
    DISTRICT = "district"
    COUNTY = "county"
    POSTCODE = "postcode"


class QueryConstructor:
    """A wrapper around HM Land Registry SparQL queries."""

    def __init__(self):
        self.endpoint = "https://landregistry.data.gov.uk/landregistry/sparql"
        try:
            self.sparql = SPARQLWrapper(self.endpoint)
        except:
            raise (ValueError, "Error creating SPARQLWrapper from defined endpoint.")
        # Generic prefixes use to query land registry data
        self._prefixes = """
          prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
          prefix owl: <http://www.w3.org/2002/07/owl#>
          prefix xsd: <http://www.w3.org/2001/XMLSchema#>
          prefix sr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>
          prefix ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
          prefix lrppi: <http://landregistry.data.gov.uk/def/ppi/>
          prefix skos: <http://www.w3.org/2004/02/skos/core#>
          prefix lrcommon: <http://landregistry.data.gov.uk/def/common/>
        """
        self._loc = ""
        self._vars = ""
        self._transx = "?transx "
        self._out_params = "SELECT "
        self._ordering = "ORDER BY "
        self._query = ""
        self._is_constructed = False
        self._location_added = False

    # Filters that can be applied to the query
    def location(self, location_data: dict) -> None:
        """Constructs partial query, adding the location parameters to the search.

        Arguments:
          location_data (dict): key-value pairs identifying the data about
           the address to be searched.

        The available criteria for search are shown in LocationCriteria. The key must match
        the name of the num entry:

          Parameter Options:
            - HOUSENUM
            - FLATNUM
            - STREET
            - TOWN
            - DISTRICT
            - COUNTY
            - POSTCODE
        """
        for item in AddressQueryParams:
            if location_data.get(item.name.lower()):
                self._vars = (
                    self._vars
                    + f"VALUES ?{item.value} {{{location_data.get(item.name.lower()).upper()}^^xsd:string}}\n"
                )
                self._loc = (
                    self._loc
                    + f"?{UKPPIQueryParams.PROPERTYADDRESS.name.lower()} lrcommon:{item} ?{item.value}.\n"
                )
        self._location_added = True

    def date_range(self) -> None:
        pass

    def query_parameters(
        self, opts: Iterable[UKPPIQueryParams | AddressQueryParams] | None = None
    ) -> None:
        """

        Arguments:
          opts (Iterable | None): Contains the string names of the output query
           parameters that will be searched for in the "WHERE" section of the
           query.
        """
        if opts is None:
            # Just return all of the data
            self._out_params = self._out_params + "*"
            # Add all PPI parameters to query
            for item in UKPPIQueryParams:
                self._transx = (
                    self._transx + f"lrppi:{item.value} ?{item.name.lower()};\n"
                )

            self._transx = self._transx + "\n\n"
            # Add all address parameters to get from the query
            for item in AddressQueryParams:
                self._transx = (
                    self._transx
                    + f"OPTIONAL {{?{UKPPIQueryParams.PROPERTYADDRESS.name.lower()} lrcommon:{item.value} ?{item.value}}}\n"
                )
            return
        # If opts supplied, just add those specified.
        for opt in opts:
            self._out_params = self._out_params + f"?{opt.name} "

        self._is_constructed = True

    def ordering(self, param: str | None = None):
        """Specify search parameter that governs ordering of the results."""
        if param is None:
            self._ordering = self._ordering + "?amount"
            return

        self._ordering + self._ordering + f"?{param}"

    def query(self):
        """Construct the query from individual components"""

        if not self._location_added:
            raise (
                NotImplementedError,
                "Geographical information specifying the query must be supplied.",
            )
        # Set other query parameters
        if not self._is_constructed:
            self.query_parameters()
            self.ordering()

        # Construct the query
        self._query = f"""
          # Key Prefixes required for the query
          {self._prefixes}
          
          # Parameters we want present in the output
          {self._out_params}
        
          WHERE
          {{
            # The actual filter values in our query
            {self._vars}
            
            # Query the address from the postcode
            {self._loc}
            
            # Get transaction data based on address and expand address data to get specifics
            {self._transx}
          }}
          # Finally, set the ordering
          {self._ordering}
        """

        # Set the SPARQL query
        self.sparql.setQuery(self._query)

        # Set the return format to JSON
        self.sparql.setReturnFormat(CSV)

        # Execute the query and parse the results
        self.results = self.sparql.query().convert()
        self.df = pd.read_csv(io.BytesIO(self.results))


async def get_house_data(postcodes: PostcodeResponseSchema):
    # Change to singleton or functional?

    query = QueryConstructor()
    location_data = {"postcode": " ".join([f"'{p.full_postcode}'" for p in postcodes])}
    query.location(location_data)
    query.query()
    # TODO: This is where we can perform calculations to get data that we want to plot
    return await aggregate_data(query.df, postcodes)


async def aggregate_data(df: pd.DataFrame, postcodes: list) -> list[LandRegistrySchema]:
    res = [None] * len(postcodes)
    for i, p in enumerate(postcodes):
        mask = df["postcode"] == p.full_postcode
        reduced = df[mask]
        data = {
            "full_postcode": p.full_postcode,
            "district_postcode": p.district_postcode,
            "subarea_postcode": p.subarea_postcode,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "sold_prices": reduced["amount"].values,
            "dates": reduced["date"].values,
        }
        res[i] = LandRegistrySchema(**data)
    return res


if __name__ == "__main__":
    # query_land_registry_data()
    query = QueryConstructor()

    # The options for the query HOUSENUM, FLATNUM, STREET, TOWN, DISTRICT, COUNTY, POSTCODE
    location_data = {"postcode": "CA10 3EX"}
    query.location(location_data)
    query.query()

    query.df.plot.hist(column=["amount"], bins=10000)
    plt.xlim(0, 1e6)
    plt.savefig("results/price_distributions.png")
