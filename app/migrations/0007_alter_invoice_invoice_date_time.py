# Generated by Django 5.0.1 on 2024-01-31 21:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_invoice_invoice_date_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 31, 21, 32, 25, 419543)),
        ),
    ]
