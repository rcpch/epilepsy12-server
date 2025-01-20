# python imports
import os

# django imports
from django.db import migrations

# from django.apps import apps as django_apps
from django.apps import apps as django_apps
from django.contrib.gis.utils import LayerMapping

Country = django_apps.get_model("epilepsy12", "Country")

# Auto-generated `LayerMapping` dictionary for JerseyBoundary model
jerseyboundary_mapping = {
    "boundary_identifier": "GID_0",
    "name": "COUNTRY",
    "geom": "MULTIPOLYGON",
}

# Get the path to the shape file
app_config = django_apps.get_app_config("epilepsy12")
app_path = app_config.path
jersey_shp_file_path = os.path.join(
    app_path, "shape_files", "gadm41_JEY_shp", "gadm41_JEY_0.shp"
)


def load_jersey_shape_file_mapping(apps, schema_editor):
    """
    Load the Jersey shape file mapping into the database
    """

    # Load the Jersey shape file mapping into the database
    lm = LayerMapping(
        Country,
        jersey_shp_file_path,
        jerseyboundary_mapping,
        transform=True,
        source_srs=4326,
        encoding="utf-8",
    )
    # Note that the target srs is 27700 so that the boundaries are in the same projection as the rest of the boundaries
    # in the database. By setting the SRID here of the source_srs to 4326, the LayerMapping will automatically transform
    # the boundaries to the target srs of 27700.

    lm.save(strict=True, verbose=True)


class Migration(migrations.Migration):

    dependencies = [
        ("epilepsy12", "0046_alter_country_bng_e_alter_country_bng_n_and_more"),
    ]

    operations = [
        migrations.RunPython(load_jersey_shape_file_mapping),
    ]
