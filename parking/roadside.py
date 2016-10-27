# -*- coding: utf-8 -*-
import pytz
from datetime import datetime

from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from parking.models import (
    ParkingLot, ParkingSpace,
    VehicleIn,  VehicleOut, RoadsideParkingRegister
)

@api_view(['GET', 'POST'])
#@permission_classes((IsAuthenticated,))
def roadside_register_api(request):
    params = request.query_params
    identifier = params.get('parking_space')

    if not identifier:
        return Response({'detail': 'please provide a valid parking space identifier.'},status=status.HTTP_400_BAD_REQUEST)

    try:
        parking_space = ParkingSpace.objects.get(identifier=identifier)
    except ParkingSpace.DoesNotExist:
        return Response({'detail': 'not found'},status=status.HTTP_404_NOT_FOUND)

    try:
        user = User.objects.get(id=2)
        #user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return Response({'detail': 'please log in.'},status=status.HTTP_400_BAD_REQUEST)

    reg = RoadsideParkingRegister.objects.create(user=user,
              parking_space=parking_space)
    reg.save()

    # fake data. for internal test only
    insert_vehicle_in_record(parking_space.parking_lot_id,parking_space.id)

    return Response({'detail': 'registered'})

# VEHICLE IN RECORD
# FAKE DATA
# FOR INTERNAL TEST
def insert_vehicle_in_record(lot_id,space_id):
    try:
        lot = ParkingLot.objects.get(id=lot_id)
        space = ParkingSpace.objects.get(id=space_id)
    except ParkingLot.DoesNotExist:
        return Response({'detail': 'parking lot not found.'},status=status.HTTP_400_BAD_REQUEST)
    except ParkingSpace.DoesNotExist:
        return Response({'detail': 'parking space not found.'},status=status.HTTP_400_BAD_REQUEST)

    v_in = VehicleIn.objects.create(parking_lot=lot,
        parking_space=space,
        type='road side',
        in_time=datetime.now().replace(tzinfo=pytz.utc),
        time_stamp=datetime.now().replace(tzinfo=pytz.utc),
        created_time=datetime.now().replace(tzinfo=pytz.utc),)
    v_in.save()

def insert_vehicle_out_record(lot_id,space_id):
    try:
        lot = ParkingLot.objects.get(id=lot_id)
        space = ParkingSpace.objects.get(id=space_id)
    except ParkingLot.DoesNotExist:
        return Response({'detail': 'parking lot not found.'},status=status.HTTP_400_BAD_REQUEST)
    except ParkingSpace.DoesNotExist:
        return Response({'detail': 'parking space not found.'},status=status.HTTP_400_BAD_REQUEST)

    v_out = VehicleOut.objects.create(parking_lot=lot,
        parking_space=space,
        type='road side',
        out_time=datetime.now().replace(tzinfo=pytz.utc),
        time_stamp=datetime.now().replace(tzinfo=pytz.utc),
        created_time=datetime.now().replace(tzinfo=pytz.utc),)
    v_out.save()

