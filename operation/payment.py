#-*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
import pytz
from pytz import timezone
from collections import OrderedDict

from guardian.shortcuts import get_objects_for_user
from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
#from django.contrib.auth.models import User

from billing.models import OfflinePayment, Bill
from billing.serializers import OfflinePaymentSerializer
from parking.models import ParkingLot

from parkhero.status_code import STATUS_CODE
from .tools import auth_check
#from .tools import login_check
from .tools import group_check

# Create your views here.
import logging
logger = logging.getLogger(__name__)

RESULTS = 40
MAX_RESULTS = 100
MAX_QUERY_DAYS = 30

 

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def offline_payment_api(request):
    user = request.user    
    parking_lot_id = request.GET.get('parking_lot_id')
    plate_number = request.GET.get('plate_number')
    start_index = request.GET.get('start_index')
    max_results = request.GET.get('max_results')

    # fill in response headers
    response = Response()
    response['Access-Control-Allow-Credentials'] = 'true'    

    # only group_user or operator_bill are allowed to perform payment query
    try:
        retval, ret_detail = auth_check(request, 'operator_bill')

        if retval == 1:
            response.data = ret_detail
            return response

        if retval != 0:
            retval, ret_detail = group_check(request.user, 'group_user')

        if retval != 0:
            response.data = ret_detail           
            return response
           
    except Exception as ex:        
        logger.error('Cannot get role for [%s]' % str(request.user))
        detail = {'detail': 'Please login as operator_bill or group_user, ex: %s.'%ex}
        detail['status'] = STATUS_CODE['database_err']
        logger.warning(detail)        
        response.data = detail        
        return response

    now = datetime.now(pytz.utc)
    before = now + timedelta(days=-MAX_QUERY_DAYS)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')
    try:
        start = int(start_index)
        if start < 0:
            start = 0
    except TypeError:
        start = 0

    m = RESULTS
    if max_results:
        m = int(max_results)
        if m > MAX_RESULTS:
            m = MAX_RESULTS
        if m < 0:
            m = RESULTS
    # retrieve data from specified parking lots
    role_list = ret_detail
    detail = {}
    detail['kind'] = 'operation#offline_payments'

    if 'group_user' in role_list and 'operator_bill' not in role_list:
        # get parking lot list
        logger.info('username[%s]' % user.username)
        specparklots = get_objects_for_user(user, "parking.act_analyse_parkinglot")
        
        try:            
            offline_payments = OfflinePayment.objects.filter(parking_lot_id__in=specparklots).filter(payment_time__gt=before_str).filter(id__gt=start).order_by('-payment_time')[0:m]
            if not offline_payments.exists():
                logger.error('No offline payment record.')                      
                detail['records'] = []
                detail['status'] = STATUS_CODE['non_offlinepay_record']
                logger.warning(detail)
                response.data = detail
                return response

        except OfflinePayment.DoesNotExist:            
            logger.error('No offline payment record for operator[%s]' % user.username)
            detail['records'] = []
            detail['status'] = STATUS_CODE['non_offlinepay_record']
            response.data = detail
            return response
        except Exception as ex:
            detail['records'] = None
            detail['detail'] = "%s"%ex
            detail['status'] = STATUS_CODE['database_err']
            logger.warning(detail)
            response.data = detail
            return response
            
    elif 'operator_bill' in role_list:
        try:            
            offline_payments = OfflinePayment.objects.filter(payment_time__gt=before_str).filter(id__gt=start).order_by('-payment_time')[0:m]
            if not offline_payments.exists():
                logger.error('No offline payment record.')                      
                detail['records'] = []
                detail['status'] = STATUS_CODE['non_offlinepay_record']
                response.data = detail
                return response

        except OfflinePayment.DoesNotExist:
            #if isinstance(ex, OfflinePayment.DoesNotExist):
            logger.error('No offline payment record for operator[%s]' % user.username)
            detail['records'] = []
            detail['status'] = STATUS_CODE['non_offlinepay_record']
            response.data = detail
            return response
        except Exception as ex:
            #else:
            detail['detail'] = "%s"%ex
            detail['status'] = STATUS_CODE['database_err']
            response.data = detail
            return response    

    serializer = OfflinePaymentSerializer(offline_payments,many=True)
    data = serializer.data
    logger.info("data: %s"%data)
    parking_lot_ids = list(set([i['parking_lot'] for i in serializer.data]))    
    try:            
        parkinglots = ParkingLot.objects.filter(id__in = parking_lot_ids)
        lots_id2name = {i.id: i.name for i in parkinglots}
        for i in data: 
            i['id'] = i['parking_lot']
            i['parking_lot'] = lots_id2name[i['parking_lot']]
    except Exception as ex:
        logger.error('Can not find parking lot has id[%s]' % parking_lot_ids)
        for i in data: 
            i['id'] = i['parking_lot']
            i['parking_lot'] = ''    

    detail['records'] = data
    detail['status'] = STATUS_CODE['success']
    response.data = detail
    return response
    

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def online_payment_api(request):
    user = request.user
    id = request.GET.get('id')
    parking_lot_id = request.GET.get('parking_lot_id')
    plate_number = request.GET.get('plate_number')
    start_index = request.GET.get('start_index')
    max_results = request.GET.get('max_results')

    # fill in response headers
    response = Response()
    response['Access-Control-Allow-Credentials'] = 'true'

    # only group_user or operator_bill are allowed to perform payment query
    try:        
        retval, ret_detail = auth_check(request, 'operator_bill')

        if retval == 1:
            response.data = ret_detail
            return response

        if retval != 0:
            retval, ret_detail = group_check(request.user, 'group_user')

        if retval != 0:
            response.data = detail           
            return response

    except Exception as ex:
        logger.error('Cannot get role for [%s]' % str(request.user))
        detail = {'detail': '%s.'%ex}        
        detail['status'] = STATUS_CODE['non_right']
        logger.warning(response.data)
        response.data = detail
        return response

    now = datetime.now(pytz.utc)
    before = now + timedelta(days=-MAX_QUERY_DAYS)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')

    records = []

    # retrieve data from specified parking lots
    role_list = ret_detail
    if 'group_user' in role_list and 'operator_bill' not in role_list:
        # get parking lot list
        logger.info('username[%s]' % user.username)        
        specparklots = get_objects_for_user(user, "parking.act_analyse_parkinglot")
        try:
            online_payments = Bill.objects.filter(paid=True).filter(vehicle_in__id__in=specparklots).filter(updated_time__gt=before_str).order_by('-updated_time')
            for p in online_payments:
                #lot_id = p.vehicle_in.parking_lot_id
                #if lot_id not in p_list:
                #if lot_id not in specparklots:
                #if lot_id in specparklots:
                    utc_time = p.updated_time
                    local_time = utc_time.astimezone(timezone('Asia/Shanghai'))
                    local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
                    record = OrderedDict()                    
                    record['plate_number'] = p.vehicle_in.plate_number
                    record['payment_time'] = local_time_str
                    record['parking_lot'] = p.vehicle_in.parking_lot.name
                    record['amount'] = p.amount
                    records.append(record)

            #lot_name = p.vehicle_in.parking_lot.name
            #print('vehicle in id[%d], lot id[%d], name[%s]' % (p.vehicle_in_id,lot_id,lot_name))
            logger.info(records)

        except (Bill.DoesNotExist, Exception) as ex:
            logger.error('No online payment record for operator[%s]' % user.username)

    elif 'operator_bill' in role_list:
        try:
            online_payments = Bill.objects.filter(paid=True).filter(updated_time__gt=before_str).order_by('-updated_time')
            for p in online_payments:
                record = OrderedDict()
                utc_time = p.updated_time
                local_time = utc_time.astimezone(timezone('Asia/Shanghai'))
                local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
                record['plate_number'] = p.vehicle_in.plate_number
                record['payment_time'] = local_time_str
                record['parking_lot'] = p.vehicle_in.parking_lot.name
                record['amount'] = p.amount
                records.append(record)

            #lot_name = p.vehicle_in.parking_lot.name
            #print('vehicle in id[%d], lot id[%d], name[%s]' % (p.vehicle_in_id,p.vehicle_in.parking_lot_id,lot_name))
            logger.info(records)
        except (Bill.DoesNotExist, Exception) as ex:
            logger.error('No online payment record for operator[%s]' % user.username)
            detail = {}
            detail['kind'] = 'operation#online_payments'
            detail['records'] = records
            response.data = detail

            return response

    detail = {}
    detail['kind'] = 'operation#online_payments'
    detail['records'] = records
    detail['status'] = STATUS_CODE['success']
    response.data = detail

    return response