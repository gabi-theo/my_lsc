# Generated by Django 5.0.1 on 2024-06-27 12:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_invoice_invoice_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 27, 12, 16, 58, 113164)),
        ),
    ]