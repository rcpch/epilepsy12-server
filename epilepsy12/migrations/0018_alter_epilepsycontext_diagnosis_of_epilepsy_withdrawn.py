# Generated by Django 4.0.4 on 2022-07-28 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0017_remove_epilepsycontext_date_of_first_epileptic_seizure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epilepsycontext',
            name='diagnosis_of_epilepsy_withdrawn',
            field=models.BooleanField(default=False, null=True, verbose_name='has the diagnosis of epilepsy been withdrawn?'),
        ),
    ]
