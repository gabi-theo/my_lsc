# Generated by Django 5.0.1 on 2024-01-31 20:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_invoice_invoice_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 31, 20, 57, 8, 562457)),
        ),
        migrations.AlterField(
            model_name='sessionpresence',
            name='status',
            field=models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('made_up', 'Made Up')], max_length=10),
        ),
    ]
