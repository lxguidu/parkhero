#-*- coding: utf-8 -*-
from .tools import get_parking_lots
import pytz
from datetime import datetime, timedelta

from guardian.shortcuts import get_objects_for_user

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

#from django.contrib.auth.models import User

from parking.models import ParkingLot, VehicleIn
from parking.serializers import VehicleInSerializer

from parkhero.status_code import STATUS_CODE
from .tools import auth_check

# Create your views here.
import logging
logger = logging.getLogger(__name__)

RESULTS     = 40
MAX_RESULTS = 100

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def vehicle_in_api(request):
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

    id = request.GET.get('id')
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
    

    parklots = get_objects_for_user(request.user, "parking.act_analyse_parkinglot")
    if parklot_ids:
        interparklot_ids = [ item.id for item in parklots if str(item.id) in parklot_ids]
    else:
        interparklot_ids = [ item.id for item in parklots]

    print("interparklot_ids: %s"%interparklot_ids)

    now = datetime.now(pytz.utc)    
    before = now + timedelta(days=-7)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')

    vehiclein_infos = VehicleIn.objects.filter(in_time__gt=before_str)

    detail = {}
    detail['kind'] = 'user#vehicle_in'
    try:
        #if parklot_ids:
        if interparklot_ids:
            vehiclein_infos = vehiclein_infos.filter(parking_lot_id__in=interparklot_ids)
            #total = v_ins_all.count()

        if plate_number:        
            vehiclein_infos = vehiclein_infos.filter(plate_number__startswith=plate_number)
        
        if id:            
            vehiclein_infos = vehiclein_infos.filter(pk=id)
        
        if start > 0:
            vehiclein_infos = vehiclein_infos.filter(pk__lt = start)        
        
        vehiclein_infos = vehiclein_infos.order_by('-in_time')
        vehiclein_infos = vehiclein_infos[0:m]

        if not vehiclein_infos.exists():            
            detail['records'] = []#{'detail': 'No vehicle-in record.'}            
            detail['detail'] = 'No vehicle-in record.'
            detail['status'] = STATUS_CODE['non_vehiclein_record']

            return Response(detail)

        serializer = VehicleInSerializer(vehiclein_infos, many=True)        
        parklot_ids = list(set([i['parking_lot'] for i in serializer.data]))
    except VehicleIn.DoesNotExist:
        logger.error('Can not find vehicle-in records, ex: %s.'%ex)
        #if not isinstance(ex, VehicleIn.DoesNotExist):
        detail['records'] = []#{'detail': 'No vehicle-in record.'}            
        detail['detail'] = 'No vehicle-in record.'
        detail['status'] = STATUS_CODE['non_vehiclein_record']
        return Response(detail)
    except Exception as ex:
        detail['records'] = []           
        detail['detail'] = '%s.'%ex
        detail['status'] = STATUS_CODE['database_err']
        return Response(detail)

    
    try:
        parkinglots = ParkingLot.objects.filter(id__in = parklot_ids)
        lots_id2name = {i.id: i.name for i in parkinglots}
        vehiclein_data = serializer.data
        for i in vehiclein_data:
            i['id'] = i['parking_lot'] 
            i['parking_lot'] = lots_id2name[i['parking_lot']]
    except (ParkingLot.DoesNotExist, Exception) as ex:
        logger.error('Can not find parking lot has id[%d], ex: %s' % (i.parking_lot, ex))
        vehiclein_data['detail'] = "%s."%ex
        for i in vehiclein_data:
            i['id'] = i['parking_lot']
            i['parking_lot'] = ''   
      
    #vehiclein_data['kind'] = 'user#vehicle_in'
    #vehiclein_data['status'] = STATUS_CODE['success']  
    response = Response(vehiclein_data)   
    return response