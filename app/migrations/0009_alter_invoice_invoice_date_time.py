# Generated by Django 5.0.1 on 2024-07-03 14:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_invoice_invoice_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 3, 14, 30, 57, 531073)),
        ),
    ]