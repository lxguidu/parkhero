# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 08:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0011_auto_20160626_0534'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OnlinePayment',
        ),
    ]
