# Generated by Django 4.0.4 on 2022-08-12 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0031_remove_antiepilepsymedicine_is_a_pregnancy_prevention_programme_in_place_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='management',
            name='individualised_care_plan_date',
            field=models.DateField(default=None, null=True, verbose_name='On what date was the individualised care plan put in place?'),
        ),
    ]
