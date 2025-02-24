# Generated by Django 5.1.2 on 2024-10-23 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "epilepsy12",
            "0039_historicalorganisationalauditsubmission_s01leadershiphours_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Banner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url_matcher", models.CharField(max_length=255)),
                ("html", models.TextField()),
                ("disabled", models.BooleanField(default=False)),
                (
                    "user_role_to_target",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        choices=[
                            (1, "Lead Clinician"),
                            (2, "Clinician"),
                            (3, "Administrator"),
                            (4, "RCPCH Audit Team"),
                            (7, "RCPCH Audit Children and Family"),
                        ],
                        null=True,
                    ),
                ),
            ],
        ),
    ]
