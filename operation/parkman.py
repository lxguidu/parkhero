#-*- coding: utf-8 -*-
from .tools import generate_key
from datetime import datetime

import pytz
#from pytz import timezone
from collections import OrderedDict

import guardian
from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User


from parking.models import ParkingLot
from parking.serializers import (
    ParkingLotSerializer, ParkingLotSerializer2
)
from parkhero.status_code import STATUS_CODE

# Create your views here.
import logging
logger = logging.getLogger(__name__)

TZ = pytz.timezone('Asia/Shanghai')


PRIVATE_KEY_SUFFIX = '_pri_key.pem'
PRIVATE_KEY_PKCS8_SUFFIX = '_pri_key_pkcs8.pem'
PUBLIC_KEY_SUFFIX = '_pub_key.pem'


class ParkLot(APIView):
    # ret: 0 - success, 1 - cant login, 2 - can login, but no right
    def auth_check(self, request):
        logger.info("login as user[%s]"%request.user)
        if not request.user.is_authenticated():
            detail = {'detail': 'Please login.'}
            detail['status'] = STATUS_CODE['need_login']            
            return 1, detail

        # only operator_parkinglot are allowed to operate on parking lot objects    
        role_list = [ i['name'] for i in request.user.groups.values()]
        logger.info('Role list[%s]' % role_list)        
        if 'operator_parkinglot' not in role_list:
            logger.error('Please login as operator_parkinglot.')
            detail = {'detail': 'Please login as operator_parkinglot.'}            
            detail['status'] = STATUS_CODE['non_right']
            return 2, detail     

        return 0, None    

    # remove an parklot
    @permission_classes((IsAuthenticated,))
    def delete(self, request, format=None):  
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)

        logger.info('user[%s] in parklot delete -- added by justin.tan' % request.user)                

        # fill in response headers
        response = Response()
        response['Access-Control-Allow-Credentials'] = 'true'

        # delete a parking lot
        data = request.data
        parklotid = data.get('parklotid')
        if not parklotid:
            detail = {'detail': 'Please provide the parking lot id.'}
            detail['status'] = STATUS_CODE['lostparam']            
            logger.warning(detail)
            response.data = detail
            return response

        try:
            parklot = ParkingLot.objects.get(id=parklotid)
            parklot.is_active = False
            parklot.save()
            msg = ('parking lot[%s] deleted' % parklotid)
            detail = {'detail': msg}
            detail['status'] = STATUS_CODE['success']
            response.data = detail
            return response
        except ParkingLot.DoesNotExist:            
            detail = {"detail": "Please provide a valid parking lot id."}
            detail['status'] = STATUS_CODE['non_such_parklot']
            response.data = detail
            return response
        except Exception as ex:            
            detail = {"detail": "%s."%ex}
            detail['status'] = STATUS_CODE['database_err']
            response.data = detail
            return response            

        


    def handle_all_parklots(self, request, parklotid):
        utc_time = datetime.now(pytz.utc)
        local_time = utc_time.astimezone(TZ)
        local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')

        try:
            detail = {}
            detail['kind'] = 'operation#parking_lots'
            
            role_list = [ i['name'] for i in request.user.groups.values()]
            logger.info('Role list[%s]' % role_list)        
            if 'group_user' in role_list:
                #park_lots = guardian.shortcuts.get_objects_for_user(operator, "parking.act_analyse_parkinglot")
                parklots = guardian.shortcuts.get_objects_for_user(request.user, "parking.act_analyse_parkinglot").filter(is_active=True).order_by('id')
                #parklots = ParkingLot.objects.filter(is_active=True).filter(id__gt=parklotid).order_by('id')[0:10]
                #parklots = ParkingLot.objects.filter(is_active=True).filter(pk__in=parklotid).all().order_by('id')
            else:  
                parklots = ParkingLot.objects.filter(is_active=True).all().order_by('id')

            detail['parking_lots'] = ParkingLotSerializer2(parklots, many=True).data       
            detail['update_time'] = local_time_str
            logger.info('Total parking lots[%d].' % len(detail['parking_lots']))
            return detail
        except (ParkingLot.DoesNotExist, Exception) as ex:
            if isinstance(ex, ParkingLot.DoesNotExist):
                detail["detail"] = "The is NO parking lot."
                detail['status'] = STATUS_CODE['non_parklot']
            else:
                detail['detail'] = "%s"%ex
                detail['status'] = STATUS_CODE['database_err']

            return detail        

    def handle_one_parklot(self, request, parklotid):
        # parking lot id check
        retval, ret_detail = self.auth_check(request)
        if retval != 0:
            return ret_detail

        try:
            detail = {}
            detail['name'] = parklot.name

            parklot = ParkingLot.objects.filter(is_active=True).get(id=parklotid)
            
            detail['identifier'] = parklot.identifier
            detail['private_key'] = parklot.private_key
            detail['status'] = STATUS_CODE['success']

            logger.info('Parking lot[%s] key info.' % parklot.name)
            return detail
        except (ParkingLot.DoesNotExist, Exception) as ex:            
            detail = {'detail': 'Can not get parking lot with id %s, ex: %s.' % (id, ex)}
            if isinstance(ex, ParkingLot.DoesNotExist):
                detail['status'] = STATUS_CODE['non_such_parklot']
            else:
                detail['status'] = STATUS_CODE['database_err']

            logger.warning(detail)            
            return detail

    # query parking lots   
    @permission_classes((IsAuthenticated,))
    def get(self, request, format=None):        
        if not request.user.is_authenticated():
            detail = {'detail': 'Please login.'}
            detail['status'] = STATUS_CODE['need_login']            
            return Response(detail)

        params = request.query_params
        parklotid = params.get('parklotid')
        querytype = params.get('querytype')        # querytype: all/one
        if querytype == 'one':
            detail = self.handle_one_parklot(request, parklotid)
            return Response(detail)

        # fill in response headers
        detail = self.handle_all_parklots(request, parklotid)
        return Response(detail)


    # create a parking lot
    @permission_classes((IsAuthenticated,))    
    def post(self, request, format=None):
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)

        # fill in response headers
        response = Response()
        response['Access-Control-Allow-Credentials'] = 'true'

        try:
            data = request.data
            name = data['name']
            address = data['address']
            city_code = data['city_code']
            longitude = data['longitude']
            latitude = data['latitude']
            price = data['price']
            parking_space_total = data['parking_space_total']
        except KeyError as e:
            key = e.args[0]
            error_msg = ('Please provide a valid %s.' % key)
            detail = {'detail': error_msg}            
            detail['status'] = STATUS_CODE['lostparam']            
            logger.warning(detail)
            response.data = detail                       
            return response
            

        # parking lot name check
        try:
            lot = ParkingLot.objects.filter(is_active=True).get(name=name)
            logger.error('Duplicated parking lot name.')
            detail = {'detail': 'Duplicated parking lot name.'} 
            detail['status'] = STATUS_CODE['such_parklot_exist']
            response.data = detail            
            return response
        except (ParkingLot.DoesNotExist, Exception) as ex:
            if not isinstance(ex, ParkingLot.DoesNotExist):
                detail = {'detail': '%s.'%ex} 
                detail['status'] = STATUS_CODE['database_err']
                response.data = detail            
                return response
            pass

        utc_time = datetime.now(pytz.utc)
        local_time = utc_time.astimezone(TZ)
        identifier_pre_str = local_time.strftime('%g%m%d')
        identifier_pre_int = int(identifier_pre_str + '0000')

        try:
            lot = ParkingLot.objects.filter(is_active=True).latest('identifier')
            if identifier_pre_int < lot.identifier:
                identifier_pre_int = lot.identifier
        except (ParkingLot.DoesNotExist, Exception) as ex:
            if not isinstance(ex, ParkingLot.DoesNotExist):
                detail = {'detail': '%s.'%ex} 
                detail['status'] = STATUS_CODE['database_err']
                response.data = detail            
                return response
            logger.error('Can not find any parking lot.')

        identifier = identifier_pre_int + 1

        lot = ParkingLot()
        lot.name = name
        lot.address = address
        lot.city_code = city_code
        lot.longitude = longitude
        lot.latitude = latitude
        lot.price = price
        lot.parking_space_total = parking_space_total
        lot.type = '封闭'
        lot.identifier = identifier

        # generate rsa key pair
        key_name = str(identifier)
        private_key_name = key_name + PRIVATE_KEY_SUFFIX
        private_key_pkcs8_name = key_name + PRIVATE_KEY_PKCS8_SUFFIX
        public_key_name = key_name + PUBLIC_KEY_SUFFIX

        try:
            # generate key pair
            generate_key(key_name)

            # read key
            with open(private_key_pkcs8_name, 'rb') as private_file:
                pri_data = private_file.read()

            private_file.close()

            with open(public_key_name, 'rb') as public_file:
                pub_data = public_file.read()

            public_file.close()

        except Exception as ex:
            detail = {'detail': '%s.'%ex} 
            detail['status'] = STATUS_CODE['unknown_err']
            response.data = detail            
            return response

        print(pri_data)
        print(pub_data)
        lot.private_key = pri_data
        lot.public_key = pub_data

        try:
            # write to database            
            lot.save()
        except Exception as ex:
            detail = {'detail': '%s.'%ex} 
            detail['status'] = STATUS_CODE['database_err']
            response.data = detail            
            return response        
        

        logger.info('Parking lot[%s] added.' % name)
        detail = {'detail': 'parking lot[%s] added.'% name}
        detail['status'] = STATUS_CODE['success']
        response.data = detail
        return response

    # update a parking lot
    @permission_classes((IsAuthenticated,))   
    def put(self, request, format=None):
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)

        # fill in response headers
        response = Response()
        response['Access-Control-Allow-Credentials'] = 'true'
        try:
            data = request.data
            parklotid = data['parklotid']
            name = data['name']
            address = data['address']
            city_code = data['city_code']
            longitude = data['longitude']
            latitude = data['latitude']
            price = data['price']
            parking_space_total = data['parking_space_total']

        except KeyError as e:
            key = e.args[0]
            error_msg = ('Please provide a valid %s.' % key)
            detail = {'detail': error_msg}
            detail['status'] = STATUS_CODE['lostparam']
            response.data = detail            
            return response

        # parking lot id check
        try:
            lot = ParkingLot.objects.filter(is_active=True).get(id=parklotid)
        except (ParkingLot.DoesNotExist, Exception) as ex:
            detail = {'detail': 'Can not get parking lot with id[%s].' % parklotid}
            detail['status'] = STATUS_CODE['non_such_parklot']
            response.data = detail
            return response

        lot.name = name
        lot.address = address
        lot.city_code = city_code
        lot.longitude = longitude
        lot.latitude = latitude
        lot.price = price
        lot.parking_space_total = parking_space_total
        try:
            lot.save()
        except Exception as ex:
            detail = {'detail': '%s'%ex}
            detail['status'] = STATUS_CODE['database_err']
            response.data = detail
            return response

        logger.info('Parking lot[%s] updated.' % name)
        response.data = {'success': 'parking lot updated'}
        return response
