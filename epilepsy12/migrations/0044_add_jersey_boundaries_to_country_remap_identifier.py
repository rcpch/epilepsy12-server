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
        transform=False,
        encoding="utf-8",
    )

    lm.save(strict=True, verbose=True)


class Migration(migrations.Migration):

    dependencies = [
        ("epilepsy12", "0043_alter_country_bng_e_alter_country_bng_n_and_more"),
    ]

    operations = [
        migrations.RunPython(load_jersey_shape_file_mapping),
    ]
