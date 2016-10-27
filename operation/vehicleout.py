#-*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from guardian.shortcuts import get_objects_for_user
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

#from django.contrib.auth.models import User

from parking.models import ParkingLot, VehicleOut
from parking.serializers import VehicleOutSerializer

from parkhero.status_code import STATUS_CODE
from .tools import auth_check

# Create your views here.
import logging
logger = logging.getLogger(__name__)

RESULTS     = 40
MAX_RESULTS = 100

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def vehicle_out_api(request):  
    try:        
        retval, retdetail = auth_check(request, 'group_user')
        if retval != 0:
            response.data = retdetail
            return response
    except Exception as ex:
        logger.error('Cannot get role for [%s]' % str(request.user))
        detail = {'detail': '%s.'%ex}        
        detail['status'] = STATUS_CODE['non_right']
        logger.warning(response.data)
        response.data = detail
        return response

    parklot_ids = request.GET.get('parking_lot_id')
    plate_number = request.GET.get('plate_number')
    start_index = request.GET.get('start_index')
    max_results = request.GET.get('max_results')

    m = RESULTS
    start = 0

    try:
        if max_results:
            m = int(max_results)
            if m > MAX_RESULTS:
                m = MAX_RESULTS
            if m < 0:
                m = RESULTS

        if start_index:
            start = int(start_index)
            if start < 0:
                start = 0
    except Exception as ex:
        start = 0
        m = RESULTS 

    now = datetime.now(pytz.utc)    
    before = now + timedelta(days=-7)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')

    parklots = get_objects_for_user(request.user, "parking.act_analyse_parkinglot")
    if parklot_ids:
        interparklot_ids = [ item.id for item in parklots if str(item.id) in parklot_ids]
    else:
        interparklot_ids = [ item.id for item in parklots]


    print("interparklot_ids: %s"%interparklot_ids)
    
    vehicleout_infos = VehicleOut.objects.filter(out_time__gt=before_str)
    detail = {}
    detail['kind'] = 'user#vehicle_out'
    try:
        #if parking_lot_id:
        if interparklot_ids:
            vehicleout_infos = vehicleout_infos.filter(parking_lot_id__in=interparklot_ids)
            
        if plate_number:            
            vehicleout_infos = vehicleout_infos.filter(plate_number__startswith=plate_number)
        
        if start > 0:
            vehicleout_infos = vehicleout_infos.filter(pk__lt = start)

        vehicleout_infos = vehicleout_infos.order_by('-out_time')
        vehicleout_infos = vehicleout_infos[0:m]
        if not vehicleout_infos.exists():            
            detail['records'] = []#{'detail': 'No vehicle-out record.'}            
            detail['detail'] = 'No vehicle-out record.'
            detail['status'] = STATUS_CODE['non_vehicleout_record']
            return Response(detail)        
        
        serializer = VehicleOutSerializer(vehicleout_infos, many=True)        
        parklot_ids = list(set([i['parking_lot'] for i in serializer.data]))
    except VehicleOut.DoesNotExist:
        logger.error('Can not find vehicle-out records. ex: %s'%ex)
        #if not isinstance(ex, VehicleOut.DoesNotExist):
        detail['records'] = []#{'detail': 'No vehicle-out record.'}            
        detail['detail'] = 'No vehicle-out record.'
        detail['status'] = STATUS_CODE['non_vehicleout_record']
        return Response(detail)
    except Exception as ex:
        detail['records'] = []#{'detail': 'No vehicle-out record.'}            
        detail['detail'] = '%s.'%ex
        detail['status'] = STATUS_CODE['database_err']
        return Response(detail)

    try:
        parkinglots = ParkingLot.objects.filter(pk__in = parklot_ids)
        lots_id2name = {i.id: i.name for i in parkinglots}
        vehicleout_data = serializer.data
        for i in vehicleout_data:
            i['id'] = i['parking_lot'] 
            i['parking_lot'] = lots_id2name[i['parking_lot']]
    except (ParkingLot.DoesNotExist, Exception) as ex:
        logger.error('Can not find parking lot has id[%d], ex: %s' % (i.parking_lot, ex))
        vehicleout_data['detail'] = "%s."%ex
        for i in vehicleout_data:
            i['id'] = i['parking_lot']
            i['parking_lot'] = ''
    
      
    #vehicleout_data['kind'] = 'user#vehicle_out'
    #vehicleout_data['status'] = STATUS_CODE['success']
    logger.info(vehicleout_data)  
    return Response(vehicleout_data)