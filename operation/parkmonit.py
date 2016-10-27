#-*- coding: utf-8 -*-
import pytz
from pytz import timezone
from datetime import datetime

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from parking.models import ParkingLot, VehicleIn, VehicleOut
from parking.serializers import ParkingLotSerializer

from billing.models import OfflinePayment

# Create your views here.
import logging
logger = logging.getLogger(__name__)

MAX_TIMESPAN = 30 # minutes

@api_view(['GET'])
def parkinglot_online_api(request):
    parking_lots = []
    try:
        lots = ParkingLot.objects.all()
    except ParkingLot.DoesNotExist:
        detail = {'detail': repr(e)}
        logger.error(detail)
        return Response(detail, status=status.HTTP_406_NOT_ACCEPTABLE)

    data = ParkingLotSerializer(lots,many=True).data

    for d in data:
        # vehicle-in record
        # vehicle-out record
        # offline payment record
        try:
            v_in = VehicleIn.objects.filter(parking_lot=d['id']).latest('created_time')
            v_out = VehicleOut.objects.filter(parking_lot=d['id']).latest('created_time')
            off_pay = OfflinePayment.objects.filter(parking_lot=d['id']).latest('created_time')
        except Exception as exc:
            continue

        now = datetime.now(pytz.utc)
        diff_in = int((now - v_in.created_time).total_seconds()/60)
        diff_out = int((now - v_out.created_time).total_seconds()/60)
        diff_pay = int((now - off_pay.created_time).total_seconds()/60)

        if diff_in < MAX_TIMESPAN or diff_out < MAX_TIMESPAN and diff_pay < MAX_TIMESPAN:
            d['time_to_latest_record'] = diff_in
            parking_lots.append(d)
        print('most likely time span[%d], parking lot[%s]' % (diff_in,d['name']))

    return Response({'parkinglots': parking_lots})

@api_view(['POST'])
def parkinglot_connected_api(request):    
    
    data = request.data

    try:
        identifier = str(data['identifier'])
        ip_address = data.get('ip_address')
    except KeyError as e:
        detail = {'detail': repr(e)}
        logger.error(detail)
        return Response(detail, status=status.HTTP_406_NOT_ACCEPTABLE)

    # verify the entrance
    try:
        #print('en[%s]' % en)
        lot = ParkingLot.objects.get(identifier=identifier)
    except ParkingLot.DoesNotExist as e:
        # for debug
        #pl = ParkingLot.objects.get(pk=5)
        #er = Entrance(name=en,parking_lot=pl)
        #er.save()
        detail = {'detail': repr(e)}
        logger.error(detail)
        return Response(detail, status=status.HTTP_406_NOT_ACCEPTABLE)
    data = ParkingLotSerializer(lot).data
    data['ip_address'] = ip_address
    data['updated_time'] = datetime.now(pytz.utc)
    parkinglot_connected.append(data)
    logger.info('Parking lot[%s] connected.' % lot.name)
    logger.debug(lot)
    return Response({'success':'connected'})

@api_view(['POST'])
def parkinglot_disconnected_api(request):
    return Response({'success':'disconnected'})