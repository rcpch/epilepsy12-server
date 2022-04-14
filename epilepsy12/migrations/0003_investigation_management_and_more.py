# Generated by Django 4.0 on 2022-04-14 20:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0002_alter_case_index_of_multiple_deprivation_quintile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Investigation_Management',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rescue_medicine_type', models.CharField(choices=[('BMZ', 'Buccal midazolam'), ('RDZ', 'Rectal diazepam'), ('Oth', 'Other')], max_length=3, verbose_name='Type of rescue medicine prescribed')),
                ('rescue_medicine_other', models.CharField(max_length=100, verbose_name='Other documented rescue medicine previously not specified.')),
                ('rescue_medicine_start_date', models.DateField(verbose_name='date rescue medicine prescribed/given.')),
                ('rescue_medicine_stop_date', models.DateField(default=None, verbose_name='date rescue medicine stopped if known.')),
                ('rescue_medicine_status', models.BooleanField(verbose_name='status of rescue medicine prescription.')),
                ('rescue_medicine_notes', models.CharField(max_length=250, verbose_name='additional notes relating to rescue medication.')),
                ('eeg_indicated', models.BooleanField(default=True)),
                ('eeg_request_date', models.DateTimeField()),
                ('eeg_performed_date', models.DateTimeField()),
                ('twelve_lead_ecg_status', models.BooleanField(default=False)),
                ('ct_head_scan_status', models.BooleanField(default=False)),
                ('mri_brain_date', models.DateField()),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment', to='epilepsy12.assessment')),
            ],
            options={
                'verbose_name': 'Investigations and Managment',
                'verbose_name_plural': 'Investigations and Managment Milestones',
            },
        ),
        migrations.RemoveField(
            model_name='rescuemedicine',
            name='assessment',
        ),
        migrations.RemoveField(
            model_name='rescuemedicine',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='rescuemedicine',
            name='updated_by',
        ),
        migrations.DeleteModel(
            name='Investigations',
        ),
        migrations.DeleteModel(
            name='RescueMedicine',
        ),
    ]
