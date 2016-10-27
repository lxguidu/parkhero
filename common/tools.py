# -*- coding: utf-8 -*-
import base64
import binascii
import logging
from collections import OrderedDict
from datetime import datetime

from django.db import transaction
from django.contrib.auth import authenticate, login

from rest_framework import status
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication,
    get_authorization_header
)
from rest_framework.decorators import (
    authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from parkhero.status_code import STATUS_CODE
from userprofile.models import UserProfile

logger = logging.getLogger(__name__)

def md5Encode(password):
    import hashlib
    m = hashlib.md5(password.encode(encoding="utf-8"))
    return m.hexdigest()


# ret: 0 - success, 1 - cant login, 2 - can login, but no admin
def login_check(request):
    """
    app api
    """
    credential = False
    logger.debug(request.META)
    
    auth = get_authorization_header(request).split()

    if not auth or auth[0].lower() != b'basic':
        error = 'No basic header. No credentials provided.'

    if len(auth) == 1:
        error = 'Invalid basic header. No credentials provided.'
    elif len(auth) > 2:
        error = 'Invalid basic header. Credentials string should not contain spaces.'

    logger.info(auth)

    try:
        auth_parts = base64.b64decode(auth[1]).decode('utf-8').partition(':')
        credential = True
    except (TypeError, UnicodeDecodeError, binascii.Error, Exception) as ex:
        error = 'Invalid basic header. Credentials not correctly base64 encoded. exception: %s'%ex    

    if not credential:
        detail   = {"detail": error}
        detail['status'] = STATUS_CODE['errparam']        
        logger.warning(detail)
        return False, detail

    logger.info(auth_parts)

    username = auth_parts[0]
    password = auth_parts[2]
    user = authenticate(username = username, password = password)

    if user is None:        
        detail = {'detail': 'Authentication credentials were not provided.'}
        detail["status"] = STATUS_CODE['user_passwd_err']
        logger.warning(detail)
        return False, detail        
    
    login(request, user)
    
    logger.info('User logged in[' + str(request.user) +']')
    return True, None   