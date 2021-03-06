# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 09:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userprofile', '0004_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingLotGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(max_length=50)),
                ('owner', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('parking_lot', models.ManyToManyField(to='parking.ParkingLot')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=20)),
                ('permission', models.IntegerField(default=0)),
                ('owner', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
