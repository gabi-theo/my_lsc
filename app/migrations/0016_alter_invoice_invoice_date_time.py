# Generated by Django 5.0.1 on 2024-07-02 13:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_alter_invoice_invoice_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 2, 13, 7, 48, 469495)),
        ),
    ]
