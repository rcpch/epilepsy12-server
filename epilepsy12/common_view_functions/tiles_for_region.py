from typing import Literal
import json

# django
from django.core.serializers import serialize
from django.apps import apps

# third party
#


def return_tile_for_region(
    abstraction_level: Literal[
        "icb", "nhs_england_region", "london_borough", "lhb", "country"
    ],
    organisation=None,
):
    """
    Returns geojson data for a given region.
    """
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    CountryBoundaries = apps.get_model("epilepsy12", "Country")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    LondonBorough = apps.get_model("epilepsy12", "LondonBorough")

    model = IntegratedCareBoard.objects.all()

    if abstraction_level == "nhs_england_region":
        model = NHSEnglandRegion.objects.all()
    elif abstraction_level == "country":
        model = CountryBoundaries
        if organisation:
            model = CountryBoundaries.objects.filter(
                boundary_identifier=organisation.country.boundary_identifier
            ).all()
        else:
            model = CountryBoundaries.objects.all()
    elif abstraction_level == "lhb":
        model = LocalHealthBoard.objects.all()
    elif abstraction_level == "london_borough":
        model = LondonBorough.objects.all()

    unedited_tile = serialize("geojson", model)

    geojson_dict = json.loads(unedited_tile)
    geojson_dict.pop("crs", None)

    return json.dumps(geojson_dict)
