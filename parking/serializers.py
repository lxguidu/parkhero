from rest_framework import serializers
from parking.models import ParkingLot, ParkingSpace, VehicleIn, VehicleOut

class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ('id', 'name', 'address', 'city_code',
                  'type', 'longitude', 'latitude',
                  'price', 'parking_space_total', 'parking_space_available',
                  'image',
                 )

class ParkingLotSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ('id', 'identifier', 'name', 'address', 'city_code',
                  'type', 'longitude', 'latitude',
                  'price', 'parking_space_total', 'parking_space_available',
                  'image',
                 )

class ParkingSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpace

class VehicleInSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleIn
        fields = ('id','plate_number','parking_card_number','in_time','parking_lot',)

class VehicleOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleOut
        fields = ('id','plate_number','parking_card_number','out_time','parking_lot',)

