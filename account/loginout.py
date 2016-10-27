#-*- coding: utf-8 -*-

import base64
import binascii
import random
import pytz

from collections import OrderedDict

from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group, Permission

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication,
    get_authorization_header
)
from rest_framework.permissions import IsAuthenticated

from parkhero.status_code import STATUS_CODE

import logging
logger = logging.getLogger(__name__)

# Create your views here.

@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def login_api(request, format=None):
    auth = get_authorization_header(request).split()

    if not auth or auth[0].lower() != b'basic':
        error = 'No basic header. No credentials provided.'

    if len(auth) == 1:
        error = 'Invalid basic header. No credentials provided.'
    elif len(auth) > 2:
        error = 'Invalid basic header. Credentials string should not contain spaces.'

    logger.info(auth)

    credential = False
    #if not credential:
    try:        
        auth_parts = base64.b64decode(auth[1]).decode('utf-8').partition(':')
        logger.info(auth_parts)
        username = auth_parts[0]
        password = auth_parts[2]
        user = authenticate(username = username, password = password)
        login(request, user)
        credential = True
    except (TypeError, UnicodeDecodeError, binascii.Error, Exception):
        error = 'Invalid basic header. Credentials not correctly base64 encoded.'  

    if not credential and request.user.is_authenticated():
        logger.info(request.user)
        credential = True            
    
    if not credential:
        return Response({'detail': error, 'status': STATUS_CODE['need_login']})
    '''
    if request.user is None:
        return Response({'detail': 'Authentication credentials were not provided.', 'status': STATUS_CODE['need_login']})
    '''
    #user = authenticate(username=username, password=password)
    logger.info('User logged in[' + str(request.user) +']')
    content = {
        'user': str(request.user),  # `django.contrib.auth.User` instance.
        'auth': str(request.auth),  # None
    }

    #groups = Group.objects.filter(owner=request.user)
    #if request.user.is_active:
    try:    
        groups = request.user.groups.values()
        groupnames = []
        for item in groups:
            groupnames.append(item['name'])
        
        if str(request.user) == 'sysadmin':
            groupnames.append('sysadmin')
        
        content['groupnames'] = groupnames
    
    except (Group.DoesNotExist, Exception) as ex:
        logger.error('Cannot get role for [%s], ex: %s' % (str(request.user), ex))        
        pass    

    content['detail'] = "Successfully logged in."
    content['status'] = STATUS_CODE["success"]
    response = Response(content)    
    return response

@api_view(['GET', 'POST'])
def logout_api(request):
    auth_logout(request)
    detail = {'detail': "Successfully logged out."}
    detail['status'] = STATUS_CODE["success"]
    return Response(detail)    