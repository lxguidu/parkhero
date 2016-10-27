#-*- coding: utf-8 -*-
from collections import OrderedDict

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group, Permission
from datetime import datetime

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication    
)
from rest_framework.views import APIView

from common.tools import md5Encode
from parkhero.status_code import STATUS_CODE

from account.models import VerificationCode

import logging
logger = logging.getLogger(__name__)

class LoginPassword(APIView):

    def post(self, request, format=None):
        data = request.data
        print(request.data)   

        try:
            phone_number = data['phone_number']    
            password = data['password']
            verification_code = data['verification_code']    
        except KeyError as e:
            detail = {'detail': repr(ex)}
            detail['status'] = STATUS_CODE["errparam"]
            return Response(detail)               

        # check verification code
        try:
            vc = VerificationCode.objects.get(phone_number=phone_number)
        except (VerificationCode.DoesNotExist, Exception) as ex:
            if isinstance(ex, VerificationCode.DoesNotExist):
                detail = {'detail': 'Please wait a moment or re-enter verification code.'}
                detail['status'] = STATUS_CODE["verify_code_wait"]
                return Response(detail)

            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            return Response(detail)

        time_diff = datetime.now() - vc.created_time.replace(tzinfo=None)
        if int(time_diff.total_seconds()) > 600:
            try:
                vc.delete()
                detail = {'detail': 'Verification code has expired.'}
                detail['status'] = STATUS_CODE["verify_code_expired"]
                return Response(detail)
            except Exception as ex:
                detail = {'detail': 'Database error occur: %s.'%ex}
                detail['status'] = STATUS_CODE["database_err"]
                return Response(detail)

        if vc.verification_code != verification_code:
            detail = {'detail': 'Verification code is invalid.'}
            detail['status'] = STATUS_CODE["verify_code_invalid"]
            return Response(detail)

        # phone number check
        try:
            user = User.objects.get(username=phone_number)
            vc.delete()
            user.set_password(password)
            user.save()
            detail = {"detail": "Successfully reset the password"}
            detail['status'] = STATUS_CODE["success"] 
            return Response(detail)
        except (User.DoesNotExist, Exception) as ex:
            if isinstance(ex, User.DoesNotExist):
                detail = {"detail": "The phone number is NOT registed."}
                detail['status'] = STATUS_CODE['phone_num_notregisted']
                return Response(detail)

            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            return Response(detail)

    @permission_classes((IsAuthenticated,))
    def put(self, request, format=None):        
        data = request.data
        user = request.user

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            detail = {'detail': 'Please provide password for user[%s]' % user.username}
            detail['status'] = STATUS_CODE['lostparam'] 
            logger.error(detail)            
            return Response(detail)

        auth = authenticate(username=user.username, password=old_password)
        if auth is not None:
            try:
                user.set_password(new_password)
                user.save()
                logger.info('User[%s]\'s password changed.'%user.username)
                detail = {'detail': "Successfully updated the password"}
                detail['status'] = STATUS_CODE['success']
                return Response(detail)
            except Exception as ex:
                detail = {'detail': "%s"%ex}
                detail['status'] = STATUS_CODE['database_err']
                logger.error(detail)
                return Response(detail)
        
        #else:        
        detail = {'detail': 'The old password is not correct.'}
        detail['status'] = STATUS_CODE['user_passwd_err'] 
        logger.error(detail)
        return Response(detail)