# Generated by Django 4.2.4 on 2023-08-17 10:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0027_countrykpiaggregation_final_publication_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="countrykpiaggregation",
            name="cohort",
            field=models.PositiveSmallIntegerField(default=None),
        ),
        migrations.AddField(
            model_name="icbkpiaggregation",
            name="cohort",
            field=models.PositiveSmallIntegerField(default=None),
        ),
        migrations.AddField(
            model_name="nhsregionkpiaggregation",
            name="cohort",
            field=models.PositiveSmallIntegerField(default=None),
        ),
        migrations.AddField(
            model_name="openukkpiaggregation",
            name="cohort",
            field=models.PositiveSmallIntegerField(default=None),
        ),
        migrations.AddField(
            model_name="organisationkpiaggregation",
            name="cohort",
            field=models.PositiveSmallIntegerField(default=None),
        ),
        migrations.AddField(
            model_name="trustkpiaggregation",
            name="cohort",
            field=models.PositiveSmallIntegerField(default=None),
        ),
        migrations.AlterField(
            model_name="countrykpiaggregation",
            name="open_access",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="icbkpiaggregation",
            name="open_access",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="nhsregionkpiaggregation",
            name="open_access",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="openukkpiaggregation",
            name="open_access",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="organisationkpiaggregation",
            name="open_access",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="trustkpiaggregation",
            name="open_access",
            field=models.BooleanField(default=False),
        ),
    ]
