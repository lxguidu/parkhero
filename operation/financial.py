#-*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from pytz import timezone

from guardian.shortcuts import get_objects_for_user
from rest_framework import status
from rest_framework.decorators import (
    authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.models import OfflinePayment, Bill
from billing.serializers import OfflinePaymentSerializer
from parking.models import ParkingLot
from django.db.models import Sum

from parkhero.status_code import STATUS_CODE
from .tools import auth_check
#from .tools import login_check
from .tools import group_check

# Create your views here.
import logging
logger = logging.getLogger(__name__)


class Finance(APIView):
    def auth_check(self, request):
        try:
            retval, ret_detail = auth_check(request, 'operator_bill')

            if retval == 1:
                return retval, ret_detail

            if retval != 0:
                retval, ret_detail = group_check(request.user, 'group_user')

            if retval != 0:                
                return 2, ret_detail

            return 0, ret_detail
            
        except Exception as ex:        
            logger.error('Cannot get role for [%s]' % str(request.user))
            detail = {'detail': 'Please login as operator_bill or group_user, ex: %s.'%ex}
            detail['status'] = STATUS_CODE['database_err']
            logger.warning(detail)                   
            return 3, detail

    @permission_classes((IsAuthenticated,))
    def get(self, request, format=None): 
        retval, retdetail = self.auth_check(request)
        if retval  != 0:
            logger.warning(retdetail)
            return Response(retdetail)

        params = request.query_params
        parklotids = params.get('parklotids')        
        startdate = params.get('startdate')
        enddate = params.get('enddate')

        if not startdate or not enddate:
            detail = {'detail': "lost necessary parameter"}
            detail['status'] = STATUS_CODE['lostparam']
            return Response(detail)

        offlinepayments = OfflinePayment.objects.filter(payment_time__gt=startdate).filter(payment_time__lt=enddate)
        if parklotids:
            offlinepayments = offlinepayments.filter(parking_lot_id__in=parklotids.split(','))
        elif 'group_user' in retdetail and 'operator_bill' not in retdetail:
            specparklots = get_objects_for_user(request.user, "parking.act_analyse_parkinglot")
            offlinepayments = offlinepayments.filter(parking_lot_id__in=specparklots)

        offlinepayments = offlinepayments.order_by('-payment_time')
        detail = {}
        try:
            if not offlinepayments.exists():
                logger.error('No offline payment record for operator[%s]' % request.user.username)
                detail['records'] = []
                detail['status'] = STATUS_CODE['non_offlinepay_record']
                return Response(detail)            
        except Exception as ex:
            detail['detail'] = "%s"%ex
            detail['status'] = STATUS_CODE['database_err']
            logger.warning(detail)
            return Response(detail)

        totalfee = offlinepayments.aggregate(Sum('amount'))['amount__sum']
        offserializer = OfflinePaymentSerializer(offlinepayments,many=True)
        offlinedata = offserializer.data
        logger.info("offlinedata: %s"%offlinedata)
        parklot_ids = list(set([i['parking_lot'] for i in offserializer.data]))    

        try:            
            parklots = ParkingLot.objects.filter(id__in = parklot_ids)
            if parklots.exists():
                lots_id2name = {i.id: i.name for i in parklots}
                for i in offlinedata: 
                    i['id'] = i['parking_lot']
                    i['parking_lot'] = lots_id2name[i['parking_lot']]
            else:
                for i in offlinedata: 
                    i['id'] = i['parking_lot']
                    i['parking_lot'] = ''

        except Exception as ex:
            logger.error('Can not find parking lot has id[%s]' % parklot_ids)
            for i in offlinedata: 
                i['id'] = i['parking_lot']
                i['parking_lot'] = ''    

        detail['records'] = offlinedata
        detail['totalfee'] = totalfee
        detail['status'] = STATUS_CODE['success']        
        return Response(detail)