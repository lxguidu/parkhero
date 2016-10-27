#-*- coding: utf-8 -*-
import os
import pytz
import logging

from datetime import datetime
from pytz import timezone

from django.contrib.auth.models import User
#from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser, FormParser

from parking.models import ParkingLot

from parkhero.settings import MEDIA_ROOT
from parkhero.status_code import STATUS_CODE

from version.models import CoverPages, IndexPages, StartupPages

logger = logging.getLogger(__name__)

@api_view([ 'POST',])
def app_startup_image_api(request):
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

    logger.info('user[%s]' % request.user)

    # only operator_parkinglot are allowed to operate on parking lot objects
    #role_list = get_role_list(user)
    role_list = [ i['name'] for i in user.groups.values()]
    logger.info('Role list[%s]' % role_list)
    if 'operator_app' not in role_list:
        logger.error('Please login as operator_app.')
        detail = {'detail': 'Please login as operator_app.'}
        detail['status'] = STATUS_CODE['non_right']
        response.data = detail
        return response


    # upload an image
    if request.method == 'POST':
        utc_time = datetime.now(pytz.utc)
        local_time = utc_time.astimezone(TZ)
        local_time_str = local_time.strftime('%g%m%d%H%M%S')

        try:
            up_file = request.FILES['filename']
            index = data['index']
        except KeyError as ex:
            key = ex.args[0]
            error_msg = ('Please provide a valid %s.' % key)
            detail = {'detail': error_msg}
            detail['status'] = STATUS_CODE['errparam']
            response.data = detail            
            #response.data = {'error_detail': error_msg}
            #response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return response        

        try:
            #up_file = request.FILES['filename']
            m, ext = os.path.splitext(up_file.name)
            file_name = 'startup_page_' + local_time_str + ext
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
            image = StartupPages.objects.get_or_create(index=index)[0]
            image.file_name = file_name
            image.save()
        except Exception as ex:
            detail = {'detail': "%s"%ex}
            detail['status'] = STATUS_CODE['database_err']
            logger.warning(detail)
            response.data = detail
            return response

        logger.info('App startup image[%s] added.' % file_path)
        #response.data = {'success': 'app startup image added'}
        detail = {'detail': 'app startup image added'}
        detail['status'] = STATUS_CODE['success']
        response.data = detail
        return response



@api_view([ 'POST',])
def app_index_image_api(request):
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

    logger.info('user[%s]' % request.user)
    # only operator_parkinglot are allowed to operate on parking lot objects
    #role_list = get_role_list(user)
    role_list = [ i['name'] for i in user.groups.values()]
    logger.info('Role list[%s]' % role_list)
    if 'operator_app' not in role_list:
        logger.error('Please login as operator_app.')
        detail = {'detail': 'Please login as operator_app.'}
        detail['status'] = STATUS_CODE['non_right']
        response.data = detail
        return response

    # upload an image
    if request.method == 'POST':
        utc_time = datetime.now(pytz.utc)
        local_time = utc_time.astimezone(TZ)
        local_time_str = local_time.strftime('%g%m%d%H%M%S')

        try:
            up_file = request.FILES['filename']
            index = data['index']
        except KeyError as ex:
            key = ex.args[0]
            error_msg = ('Please provide a valid %s.' % key)
            detail = {'detail': error_msg}
            detail['status'] = STATUS_CODE['errparam']
            response.data = detail
            return response
      
        try:

            #up_file = request.FILES['filename']
            m, ext = os.path.splitext(up_file.name)
            file_name = 'index_page_' + local_time_str + ext
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
            image = IndexPages.objects.get_or_create(index=index)[0]
            image.file_name = file_name
            image.save()
        except Exception as ex:
            detail = {'detail': "%s"%ex}
            detail['status'] = STATUS_CODE['database_err']
            logger.warning(detail)
            response.data = detail
            return response

        logger.info('App index image[%s] added.' % file_path)
        detail = {'detail': 'app index image added'}
        detail['status'] = STATUS_CODE['success']
        response.data = detail
        return response


@api_view([ 'POST',])
def app_cover_image_api(request):
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

    logger.info('user[%s]' % request.user)

    # only operator_parkinglot are allowed to operate on parking lot objects
    #role_list = get_role_list(user)
    role_list = [ i['name'] for i in user.groups.values()]
    logger.info('Role list[%s]' % role_list)
    if 'operator_app' not in role_list:
        logger.error('Please login as operator_app.')
        detail = {'detail': 'Please login as operator_app.'}
        detail['status'] = STATUS_CODE['non_right']
        response.data = detail
        return response

    # upload an image
    if request.method == 'POST':
        utc_time = datetime.now(pytz.utc)
        local_time = utc_time.astimezone(TZ)
        local_time_str = local_time.strftime('%g%m%d%H%M%S')

        try:
            up_file = request.FILES['filename']
            index = data['index']
        except KeyError as ex:
            key = ex.args[0]
            error_msg = ('Please provide a valid %s.' % key)
            #response.data = {'error_detail': error_msg}
            #response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            detail = {'detail': error_msg}
            detail['status'] = STATUS_CODE['errparam']
            response.data = detail
            return response
        
        try:
            #up_file = request.FILES['filename']
            m, ext = os.path.splitext(up_file.name)
            file_name = 'cover_page_' + local_time_str + ext
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
            image = CoverPages.objects.get_or_create(index=index)[0]
            image.file_name = file_name
            image.save()
        except Exception as ex:
            detail = {'detail': "%s"%ex}
            detail['status'] = STATUS_CODE['database_err']
            logger.warning(detail)
            response.data = detail
            return response

        logger.info('App cover image[%s] added.' % file_path)
        detail = {'detail': 'app cover image added'}
        detail['status'] = STATUS_CODE['success']
        response.data = detail
        return response