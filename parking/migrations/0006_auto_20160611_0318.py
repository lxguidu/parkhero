# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-11 03:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0005_roadsideparkingregister'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiclein',
            name='notice_id',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='vehicleout',
            name='notice_id',
            field=models.CharField(max_length=40),
        ),
    ]
