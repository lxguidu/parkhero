#-*- coding: utf-8 -*-
import os

from datetime import datetime
import pytz
from pytz import timezone
from collections import OrderedDict

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser, FormParser

from django.contrib.auth.models import User

from parking.models import ParkingLot
from parkhero.settings import MEDIA_ROOT
from parkhero.status_code import STATUS_CODE

# Create your views here.
import logging
logger = logging.getLogger(__name__)

TZ = pytz.timezone('Asia/Shanghai')

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def upload_tool_info_api(request):
    parser = JSONParser
    data = request.data
    user = request.user

    # fill in response headers
    response = Response()
    response['Access-Control-Allow-Credentials'] = 'true'

    # authenticate
    if not request.user.is_authenticated():        
        detail = {'detail': 'Please login.'}
        detail['status'] = STATUS_CODE['need_login']
        response.data = detail
        return response

    # only operator_parkinglot are allowed to operate on parking lot objects
    
    #role_list = get_role_list(user)
    role_list = [ i['name'] for i in user.groups.values()]
    logger.info('Role list[%s]' % role_list)
    if 'operator_parkinglot' not in role_list:
        logger.error('Please login as operator_parkinglot.')
        detail = {'detail': 'Please login as operator_parkinglot.'}
        detail['status'] = STATUS_CODE['non_right']
        response.data = detail        
        return response    

    try:
        id = request.GET.get('id')
    except KeyError as e:
        key = e.args[0]
        error_msg = ('Please provide a valid %s.' % key)
        detail = {'detail': error_msg}            
        detail['status'] = STATUS_CODE['errparam']
        response.data = detail
        return response

    if request.method == 'GET':        

        # parking lot id check
        try:
            parklot = ParkingLot.objects.filter(is_active=True).get(id=id)
        except (ParkingLot.DoesNotExist, Exception) as ex:            
            detail = {'detail': 'Can not get parking lot with id %s, ex: %s.' % (id, ex)}
            if isinstance(ex, ParkingLot.DoesNotExist):
                detail['status'] = STATUS_CODE['non_such_parklot']
            else:
                detail['status'] = STATUS_CODE['database_err']

            logger.warning(detail)
            response.data = detail
            return response        

        upload_tool_info = OrderedDict()
        upload_tool_info['name'] = parklot.name
        upload_tool_info['identifier'] = parklot.identifier
        upload_tool_info['private_key'] = parklot.private_key
        upload_tool_info['status'] = STATUS_CODE['success']

        logger.info('Parking lot[%s] key info.' % parklot.name)
        response.data = upload_tool_info

        return response

@api_view([ 'POST',])
def parking_lot_image_api(request):
    parser = (JSONParser, MultiPartParser, FormParser,)
    data = request.data
    user = request.user

    # fill in response headers
    response = Response()
    response['Access-Control-Allow-Credentials'] = 'true'   

    # authenticate
    if not request.user.is_authenticated():        
        detail = {'detail': 'Please login.'}
        detail['status'] = STATUS_CODE['need_login']
        response.data = detail
        return response

    # only operator_parkinglot are allowed to operate on parking lot objects    
    #role_list = get_role_list(user)
    role_list = [ i['name'] for i in user.groups.values()]
    logger.info('Role list[%s]' % role_list)
    if 'operator_parkinglot' not in role_list:
        logger.error('Please login as operator_parkinglot.')       
        detail = {'detail': 'Please login as operator_parkinglot.'}
        detail['status'] = STATUS_CODE['non_right']
        response.data = detail
        return response    

    try:
        identifier = data['identifier']
    except KeyError as e:
        key = e.args[0]
        error_msg = ('Please provide a valid %s.' % key)
        detail = {'detail': error_msg}
        detail['status'] = STATUS_CODE['errparam']
        response.data = detail
        return response

    # upload an image
    if request.method == 'POST':        

        # parking lot name check
        try:
            parklot = ParkingLot.objects.filter(is_active=True).get(identifier=identifier)
        except (ParkingLot.DoesNotExist, Exception) as ex:
            logger.error('No parking lot with identifier %d' % identifier)
            #response.data = {'error_detail': 'Please provide a valid identifier.'}
            #response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            detail = {'detail': 'Can not get parking lot with id %s, ex: %s.' % (id, ex)}
            if isinstance(ex, ParkingLot.DoesNotExist):
                detail['status'] = STATUS_CODE['non_such_parklot']
            else:
                detail['status'] = STATUS_CODE['database_err']

            logger.warning(detail)
            response.data = detail            
            return response

        utc_time = datetime.now(pytz.utc)
        local_time = utc_time.astimezone(TZ)
        local_time_str = local_time.strftime('%g%m%d%H%M%S')
        try:
            up_file = request.FILES['filename']
            m, ext = os.path.splitext(up_file.name)
            file_name = str(identifier) + '_' + local_time_str + ext
            file_path = MEDIA_ROOT + file_name
            logger.info(file_path)

            destination = open(file_path, 'wb+')
            for chunk in up_file.chunks():
                destination.write(chunk)
            destination.close()
        except Exception as ex:
            detail = {'detail': "%s"%ex}
            detail['status'] = STATUS_CODE['unknown_err']
            logger.warning(detail)
            response.data = detail            
            return response

        try:
            parklot.image = file_name
            parklot.save()
        except Exception as ex:
            detail = {'detail': "%s"%ex}
            detail['status'] = STATUS_CODE['database_err']
            logger.warning(detail)
            response.data = detail
            return response

        logger.info('Parking lot image[%s] added.' % file_path)
        detail = {'detail': 'parking lot image added'}
        detail['status'] = STATUS_CODE['success']
        response.data = detail
        return response