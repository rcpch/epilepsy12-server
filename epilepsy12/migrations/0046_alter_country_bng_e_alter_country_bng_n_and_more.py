# Generated by Django 5.1.2 on 2024-11-23 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epilepsy12", "0045_alter_kpi_assessment_of_mental_health_issues_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="bng_e",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="country",
            name="bng_n",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="country",
            name="globalid",
            field=models.CharField(blank=True, max_length=38, null=True),
        ),
        migrations.AlterField(
            model_name="country",
            name="lat",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="country",
            name="long",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="country",
            name="welsh_name",
            field=models.CharField(blank=True, max_length=17, null=True),
        ),
        migrations.AlterField(
            model_name="trust",
            name="ods_code",
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
