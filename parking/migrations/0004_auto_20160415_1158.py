# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-15 03:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0003_auto_20160415_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleout',
            name='out_time',
            field=models.CharField(max_length=25),
        ),
        migrations.AlterField(
            model_name='vehicleout',
            name='time_stamp',
            field=models.BigIntegerField(default=0),
        ),
    ]
