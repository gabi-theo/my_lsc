# Generated by Django 5.0.1 on 2024-02-01 15:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_alter_invoice_invoice_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 1, 15, 6, 29, 264051)),
        ),
        migrations.AlterField(
            model_name='sessionpresence',
            name='status',
            field=models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('made_up_complete', 'Made Up Complete'), ('made_up_setup', 'Made Up Setup')], max_length=20),
        ),
    ]
