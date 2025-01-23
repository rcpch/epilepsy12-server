# Generated by Django 5.1.2 on 2024-11-23 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epilepsy12", "0048_add_jersey_general_hospital_and_relationships"),
    ]

    operations = [
        migrations.AddField(
            model_name="case",
            name="unique_reference_number",
            field=models.CharField(
                blank=True,
                help_text="This is a unique reference number for Jersey patients. It is used to identify the patient in the audit.",
                max_length=20,
                null=True,
                unique=True,
                verbose_name="Unique Reference Number (URN)",
            ),
        ),
        migrations.AddField(
            model_name="historicalcase",
            name="unique_reference_number",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="This is a unique reference number for Jersey patients. It is used to identify the patient in the audit.",
                max_length=20,
                null=True,
                verbose_name="Unique Reference Number (URN)",
            ),
        ),
        migrations.AlterField(
            model_name="case",
            name="nhs_number",
            field=models.CharField(
                blank=True,
                help_text="This is the NHS number for England and Wales. It is used to identify the patient in the audit.",
                max_length=10,
                null=True,
                unique=True,
                verbose_name="NHS Number",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcase",
            name="nhs_number",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="This is the NHS number for England and Wales. It is used to identify the patient in the audit.",
                max_length=10,
                null=True,
                verbose_name="NHS Number",
            ),
        ),
    ]
