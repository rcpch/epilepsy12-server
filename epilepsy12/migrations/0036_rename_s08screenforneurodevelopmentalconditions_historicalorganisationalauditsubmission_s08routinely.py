# Generated by Django 5.1 on 2024-10-10 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "epilepsy12",
            "0035_alter_historicalorganisationalauditsubmission_s05typicaltimetoachievespecialistadvice_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="historicalorganisationalauditsubmission",
            old_name="S08ScreenForNeurodevelopmentalConditions",
            new_name="S08RoutinelyFormallyScreenForNeurodevelopmental",
        ),
        migrations.RenameField(
            model_name="organisationalauditsubmission",
            old_name="S08ScreenForNeurodevelopmentalConditions",
            new_name="S08RoutinelyFormallyScreenForNeurodevelopmental",
        ),
        migrations.AlterField(
            model_name="historicalorganisationalauditsubmission",
            name="S10TrustMaintainADatabaseOfChildrenWithEpilepsies",
            field=models.TextField(
                blank=True,
                choices=[
                    ("YA", "Yes, for all children"),
                    ("YS", "Yes, for some children"),
                    ("N", "No"),
                ],
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="organisationalauditsubmission",
            name="S10TrustMaintainADatabaseOfChildrenWithEpilepsies",
            field=models.TextField(
                blank=True,
                choices=[
                    ("YA", "Yes, for all children"),
                    ("YS", "Yes, for some children"),
                    ("N", "No"),
                ],
                null=True,
            ),
        ),
    ]
