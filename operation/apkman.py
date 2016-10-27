#-*- coding: utf-8 -*-
import os
import logging

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser, FormParser
from django.utils.datastructures import MultiValueDictKeyError

from parkhero.settings import MEDIA_ROOT
from version.models import AndroidAppVersion

from parkhero.status_code import STATUS_CODE

logger = logging.getLogger(__name__)

@api_view([ 'POST',])
def app_package_upload_api(request):
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

    # upload a package
    if request.method == 'POST':
        try:
            package_name = data['package_name']
            up_file = request.FILES['file_name']
        except (KeyError, MultiValueDictKeyError) as ex:
            key = ex.args[0]
            error_msg = ('Please provide a valid %s.' % key)
            logger.error(error_msg)

            detail = {'detail': error_msg}
            detail['status'] = STATUS_CODE['lostparam']
            response.data = detail
            return response
        # package name check
        try:
            version = AndroidAppVersion.objects.latest('version_code')
        except AndroidAppVersion.DoesNotExist:
            logger.error('No app package with name %s' % package_name)
            detail = {'detail': 'Please provide a valid package name.'}
            detail['status'] = STATUS_CODE['non_valid_packname']
            response.data = detail 
            #response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return response

        try:
            #up_file = request.FILES['filename']
            m, ext = os.path.splitext(up_file.name)
            file_name = package_name.split('.')[0] + str(version.version_code) + '.' +package_name.split('.')[1]
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


        logger.info('app package[%s] uploaded.' % file_path)
        #response.data = {'success': 'app package uploaded'}
        detail = {'detail': 'app package uploaded'}
        detail['status'] = STATUS_CODE['success']
        response.data = detail
        return response