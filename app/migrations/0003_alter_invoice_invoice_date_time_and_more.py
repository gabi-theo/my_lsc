# Generated by Django 5.0.1 on 2024-01-28 15:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_time_courseschedule_start_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 28, 15, 23, 1, 508234)),
        ),
        migrations.AlterField(
            model_name='trainer',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='trainer',
            name='last_name',
            field=models.CharField(max_length=50),
        ),
    ]
