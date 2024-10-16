# Generated by Django 5.1 on 2024-10-16 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "epilepsy12",
            "0038_historicalorganisationalauditsubmission_submitted_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalorganisationalauditsubmission",
            name="S01LeadershipHours",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="organisationalauditsubmission",
            name="S01LeadershipHours",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
