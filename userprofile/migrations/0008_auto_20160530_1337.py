# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-30 13:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0007_operatorprofile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='operatorprofile',
            old_name='parking_lot',
            new_name='parking_lots',
        ),
    ]
