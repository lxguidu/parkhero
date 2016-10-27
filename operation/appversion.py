#-*- coding: utf-8 -*-
import os
import pytz
import logging

from datetime import datetime
from pytz import timezone
from collections import OrderedDict

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from version.models import AndroidAppVersion

from parkhero.status_code import STATUS_CODE

logger = logging.getLogger(__name__)

@api_view(['GET',  'POST',])
def app_version_api(request):
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
    if 'operator_app' not in role_list:
        logger.error('Please login as operator_app.')
        detail = {'detail': 'Please login as operator_app.'}
        detail['status'] = STATUS_CODE['non_right']
        response.data = detail
        return response

    # query latest version
    if request.method == 'GET':
        try:
            version = AndroidAppVersion.objects.latest('updated_time')
        except AndroidAppVersion.DoesNotExist:
            detail = {'detail': 'The is NO app released.'}
            detail['status'] = STATUS_CODE['non_app_release']
            #return Response(error_detail, status=status.HTTP_404_NOT_FOUND)
            response.data = detail
            return response

        response_dict = OrderedDict()
        response_dict['kind'] = 'operation#app_version'
        response_dict['version_code'] = version.version_code
        response_dict['version_name'] = version.version_name
        response_dict['package_name'] = version.package_name
        response_dict['release_date'] = version.release_date
        response_dict['release_notes'] = version.release_notes
        response_dict['update_time'] = version.updated_time
        response_dict['status'] = STATUS_CODE['success']

        response.data = response_dict
        return response

    # new version
    if request.method == 'POST':
        try:
            version_code = data['version_code']
            version_name = data['version_name']
            package_name = data['package_name']
            release_date = data['release_date']
            release_notes = data['release_notes']
        except KeyError as e:
            key = e.args[0]
            error_msg = ('Please provide a valid %s.' % key)            
            detail = {'detail': error_msg}
            detail['status'] = STATUS_CODE['errparam']
            response.data = detail                        
            return response

        try:
            version = AndroidAppVersion()
            version.version_code = version_code
            version.version_name = version_name
            version.package_name = package_name
            version.release_date = release_date
            version.release_notes = release_notes
            version.updated_time = datetime.now(pytz.utc)
            version.save()
        except Exception as ex:
            detail = {'detail': "%s"%ex}
            detail['status'] = STATUS_CODE['database_err']
            logger.warning(detail)
            response.data = detail
            return response

        logger.info('new app version added.')
        detail = {'detail': 'new app version added'}
        detail['status'] = STATUS_CODE['success'] 
        #response.data = {'success': 'new app version added'}
        response.data = detail
        return response