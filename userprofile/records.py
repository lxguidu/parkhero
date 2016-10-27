from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from collections import OrderedDict

#import requests
from random import Random
from datetime import datetime, timedelta
from urllib.parse import unquote, parse_qs

import pytz
#import hashlib
import time

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from parking.models import (
    ParkingLot, ParkingSpace, VehicleIn, VehicleOut,
)
from parking.views import get_parking_records, cacl_notice_id
from parking.roadside import insert_vehicle_out_record # INTERNAL TEST
from billing.models import (
    PrePayOrder, PrePayOrderWeChatPay, PrePayNotifyWeChatPay,
    PrePayOrderAliPay, PrePayNotifyAliPay,
    PrePayOrderUnionPay, PrePayNotifyUnionPay,
    Bill, BillNotify, Payment, OfflinePayment, MonthlyCardPayment
)
from userprofile.models import UserProfile, Vehicle
from socket_broker.client import BrokerClient

import logging
logger = logging.getLogger(__name__)

tz = pytz.timezone('Asia/Shanghai')

RESULTS     = 40
MAX_RESULTS = 100
QUERY_DAYS = 7

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def bills_api(request):
    """
    app api
    """
    user = request.user
    # DEBUG
    #user = User.objects.get(username='18002586887')
    start_index = request.GET.get('start_index')
    max_results = request.GET.get('max_results')

    mx = RESULTS
    if max_results:
        mx = int(max_results)
        if mx > MAX_RESULTS:
            mx = MAX_RESULTS
        if mx < 0:
            mx = RESULTS

    try:
        vehicles = Vehicle.objects.filter(owner=user)
    except Exception as e:
        logger.error(e)
        error_detail = {'detail': 'No valid plate number found.'}
        return Response(error_detail, status=status.HTTP_404_NOT_FOUND)

    # get plate number list
    plate_number_list = []

    for v in vehicles:
        plate_number_list.append(v.plate_number)

    # record array
    records_all = []
    now = datetime.now(pytz.utc)
    before = now + timedelta(days=-7)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')

    # DEBUG
    #plate_number_list = ['粤B853KF','粤BK3955']

    # online_payment
    try:
        online_payment = Bill.objects.filter(paid=True).filter(updated_time__gt=before_str).filter(vehicle_in__plate_number__in=plate_number_list).order_by('-updated_time')
        # manually create records
        for i in online_payment:
            record = OrderedDict()
            record['plate_number'] = i.vehicle_in.plate_number
            record['parking_lot'] = i.vehicle_in.parking_lot.name
            record['payment_type'] = 'online payment'
            record['payment_time'] = i.updated_time.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
            record['amount'] = i.amount
            records_all.append(record)
    except Bill.DoesNotExist:
        logger.error('Can NOT get online payment records.')

    # offline payment
    try:
        offline_payment = OfflinePayment.objects.filter(created_time__gt=before_str).filter(plate_number__in=plate_number_list).order_by('-created_time')
        # manually create records
        for i in offline_payment:
            record = OrderedDict()
            record['plate_number'] = i.plate_number
            record['parking_lot'] = i.parking_lot.name
            record['payment_type'] = 'offline payment'
            record['payment_time'] = i.payment_time
            record['amount'] = i.amount
            records_all.append(record)

    except OfflinePayment.DoesNotExist:
        logger.error('Can NOT get offline payment records.')

    # monthlycard payment
    try:
        monthlycard_payment = MonthlyCardPayment.objects.filter(created_time__gt=before_str).filter(plate_number__in=plate_number_list).order_by('-created_time')
        # manually create records
        for i in offline_payment:
            record = OrderedDict()
            record['plate_number'] = i.plate_number
            record['parking_lot'] = i.parking_lot.name
            record['payment_type'] = 'monthly card payment'
            record['payment_time'] = i.payment_time
            record['amount'] = i.amount
            records_all.append(record)
 
    except MonthlyCardPayment.DoesNotExist:
        logger.error('Can NOT get monthly card payment records.')

    records_all.sort(key=lambda x:x['payment_time'],reverse=True)

    if start_index:
        start = int(start_index)
        if start < 0:
            start = 0

        end = start + mx
        records = records_all[start:end]
    else:
        records = records_all[:mx]

    response_dict = OrderedDict()
    response_dict['kind'] = 'user#bills'
    response_dict['bills'] = records
    return Response(response_dict)
    return Response({'detail': 'records'})

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def prepayments_api(request):
    """
    app api
    """
    user = request.user
    # DEBUG
    #user = User.objects.get(username='18002586887')
    start_index = request.GET.get('start_index')
    max_results = request.GET.get('max_results')

    mx = RESULTS
    if max_results:
        mx = int(max_results)
        if mx > MAX_RESULTS:
            mx = MAX_RESULTS
        if mx < 0:
            mx = RESULTS

    # record array
    records = []
    now = datetime.now(pytz.utc)
    before = now + timedelta(days=-700)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')

    try:
        prepayments = PrePayOrder.objects.filter(user=user).filter(paid=True).filter(updated_time__gt=before_str).order_by('-updated_time')
        for p in prepayments:
            record = OrderedDict()
            utc_time = p.updated_time
            local_time = utc_time.astimezone(tz)
            local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
            #record['user_name'] = p.user.username
            record['payment_time'] = local_time_str
            record['payment_channel'] = p.payment_channel
            record['amount'] = p.amount
            records.append(record)

            #lot_name = p.vehicle_in.parking_lot.name
            #print('vehicle in id[%d], lot id[%d], name[%s]' % (p.vehicle_in_id,p.vehicle_in.parking_lot_id,lot_name))
        logger.info(records)
    except PrePayOrder.DoesNotExist:
        logger.error('No prepayment record for operator[%s]' % user.username)


    if start_index:
        start = int(start_index)
        if start < 0:
            start = 0

        end = start + mx
        records = records[start:end]
    else:
        records = records[:mx]

    response_dict = OrderedDict()
    response_dict['kind'] = 'user#prepayments'
    response_dict['records'] = records
    return Response(response_dict)

    return response


