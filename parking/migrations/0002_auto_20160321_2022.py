# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-21 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiclein',
            name='notice_id',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='vehicleout',
            name='notice_id',
            field=models.CharField(max_length=20),
        ),
    ]
