# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-15 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='account_balance',
            field=models.IntegerField(default=0),
        ),
    ]