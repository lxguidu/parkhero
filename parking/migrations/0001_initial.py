# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-21 02:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingLot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('identifier', models.IntegerField(default=0)),
                ('address', models.CharField(max_length=200)),
                ('city_code', models.IntegerField(default=0)),
                ('type', models.CharField(choices=[('CP', 'Common Parking Lot'), ('SP', 'Smart Parking Lot'), ('RP', 'Road-side Parking Lot')], default='CP', max_length=2)),
                ('longitude', models.FloatField(default=0)),
                ('latitude', models.FloatField(default=0)),
                ('distance', models.FloatField(default=0)),
                ('price', models.CharField(max_length=200)),
                ('parking_space_total', models.IntegerField(default=0)),
                ('parking_space_available', models.IntegerField(default=0)),
                ('private_key', models.CharField(max_length=1000)),
                ('public_key', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='ParkingSpace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=10)),
                ('type', models.CharField(choices=[('S', 'Small Parking Space'), ('M', 'Middle Parking Space'), ('L', 'Large Parking Space')], default='S', max_length=1)),
                ('floor', models.SmallIntegerField(default=1)),
                ('status', models.CharField(choices=[('A', 'Available'), ('O', 'Occupied'), ('P', 'Proprietary')], default='A', max_length=1)),
                ('parking_lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parking.ParkingLot')),
            ],
        ),
        migrations.CreateModel(
            name='VehicleIn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plate_number', models.CharField(max_length=15)),
                ('parking_card_number', models.CharField(max_length=20)),
                ('vehicle_img', models.URLField()),
                ('plate_img', models.URLField()),
                ('type', models.CharField(max_length=15)),
                ('in_time', models.DateTimeField()),
                ('time_stamp', models.DateTimeField()),
                ('notice_id', models.IntegerField(default=0)),
                ('price_list', models.CharField(max_length=1000)),
                ('parking_space_total', models.IntegerField(default=0)),
                ('parking_space_available', models.IntegerField(default=0)),
                ('created_time', models.DateTimeField()),
                ('parking_lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parking.ParkingLot')),
            ],
        ),
        migrations.CreateModel(
            name='VehicleOut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plate_number', models.CharField(max_length=15)),
                ('parking_card_number', models.CharField(max_length=20)),
                ('vehicle_img', models.URLField()),
                ('plate_img', models.URLField()),
                ('type', models.CharField(max_length=15)),
                ('out_time', models.DateTimeField()),
                ('time_stamp', models.DateTimeField()),
                ('notice_id', models.IntegerField(default=0)),
                ('price_list', models.CharField(max_length=1000)),
                ('parking_space_total', models.IntegerField(default=0)),
                ('parking_space_available', models.IntegerField(default=0)),
                ('created_time', models.DateTimeField()),
                ('parking_lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parking.ParkingLot')),
            ],
        ),
    ]
