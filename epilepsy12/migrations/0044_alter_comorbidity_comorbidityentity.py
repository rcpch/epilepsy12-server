# Generated by Django 5.1.4 on 2025-01-04 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "epilepsy12",
            "0043_alter_historicalorganisationalauditsubmission_s01jobplannedhoursperweekleadershipqiactivities_and_mo",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="comorbidity",
            name="comorbidityentity",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text={
                    "label": "What is the comorbidity?",
                    "reference": "Paediatric neurodisability outpatient diagnosis simple reference set (999001751000000105), SNOMED-CT",
                },
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="epilepsy12.comorbiditylist",
            ),
        ),
    ]
