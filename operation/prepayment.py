#-*- coding: utf-8 -*-
import pytz
from pytz import timezone
from datetime import datetime, timedelta
from collections import OrderedDict

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

#from django.contrib.auth.models import User

from billing.models import Bill, PrePayOrder
from parkhero.status_code import STATUS_CODE
from .tools import auth_check

# Create your views here.
import logging
logger = logging.getLogger(__name__)

MAX_QUERY_DAYS = 30

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def prepayment_api(request):
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
        retval, retdetail = auth_check(request, 'operator_bill')
        if retval != 0:
            response.data = retdetail
            return response
    #except Role.DoesNotExist:
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
    #if 'operator_bill' in role_list:
    detail = {}
    detail['kind'] = 'operation#prepayments'
    
    try:
        prepayments = PrePayOrder.objects.filter(paid=True).filter(updated_time__gt=before_str).order_by('-updated_time')
        for p in prepayments:
            record = OrderedDict()
            utc_time = p.updated_time
            local_time = utc_time.astimezone(timezone('Asia/Shanghai'))
            local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
            record['user_name'] = p.user.username
            record['payment_time'] = local_time_str
            record['payment_channel'] = p.payment_channel
            record['amount'] = p.amount
            records.append(record)

        #lot_name = p.vehicle_in.parking_lot.name
        #print('vehicle in id[%d], lot id[%d], name[%s]' % (p.vehicle_in_id,p.vehicle_in.parking_lot_id,lot_name))
        logger.info(records)
    except (PrePayOrder.DoesNotExist, Exception) as ex:
        if isinstance(ex, PrePayOrder.DoesNotExist):
            logger.error('No prepayment record for operator[%s]' % user.username)
        else:
            detail['records'] = records
            detail['status'] = STATUS_CODE['database_err']
            detail['detail'] = "%s"%ex
            response.data = detail
            return response

    #response_dict = OrderedDict()    
    detail['records'] = records
    detail['status'] = STATUS_CODE['success']
    response.data = detail
    return response