#-*- coding: utf-8 -*-
import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group, Permission

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


logger = logging.getLogger(__name__)

class BackPerm(APIView):
    # ret: 0 - success, 1 - cant login, 2 - can login, but no admin
    def auth_check(self, request):
        if not request.user.is_authenticated():
            detail = {'detail': 'Please login.'}
            detail['status'] = STATUS_CODE['need_login']            
            return 1, detail

        if str(request.user) != 'sysadmin':
            detail = {'detail': 'Please login as administrator'}
            detail['status'] = STATUS_CODE['non_administrator']
            return 2, detail

        return 0, None

    # remove an role
    @permission_classes((IsAuthenticated,))
    def get(self, request, format=None):
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)

        try:
            allperms = Permission.objects.all()
            perminfos = []
            for permitem in allperms:
                perminfos.append({
                    'permid'    : permitem.id,
                    'permname'  : permitem.codename,
                    'permdesc'  : permitem.name                    
                })
            detail = {'detail': 'successfully get all permissions info'}
            detail['status'] = STATUS_CODE['success']   
            detail['groupinfo'] = perminfos
            return Response(detail)
        except Exception as ex:
            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            logger.warning(detail) 
            return Response(detail)