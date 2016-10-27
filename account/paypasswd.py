#-*- coding: utf-8 -*-
import base64
import logging
from collections import OrderedDict
from datetime import datetime

from rest_framework import status
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication    
)
from rest_framework.decorators import (
    authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import VerificationCode
from common.tools import md5Encode
from parkhero.status_code import STATUS_CODE
from userprofile.models import UserProfile

logger = logging.getLogger(__name__)

class PaymentPassword(APIView):

    @permission_classes((IsAuthenticated,))
    def post(self, request, format=None):
        #parser = JSONParser    
        data = request.data
        user = request.user
        logger.info(data)
        try:
            phone_number = user.username    
            password = data.get('password')
            verification_code = data.get('verification_code')        
        except KeyError as ex:
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
            up = UserProfile.objects.get(user=user)
            vc.delete()
            password = base64.b64decode(password).decode("utf-8")
            up.payment_password = md5Encode(password)
            up.save()
        except (UserProfile.DoesNotExist, Exception) as ex:
            if isinstance(ex, UserProfile.DoesNotExist):
                detail = {'detail': 'Failed to get user profile'}
                detail['status'] = STATUS_CODE["user_no_profile"]
                return Response(detail)

            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            return Response(detail)

        
        detail = {'detail': 'Successfully reset the payment password'}
        detail['status'] = STATUS_CODE["success"]
        return Response(detail)

    
    @permission_classes((IsAuthenticated,))
    def put(self, request, format=None):
        #parser = JSONParser        
        data = request.data
        user = request.user

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            detail = {'detail': 'Please provide password for user[%s]' % user.username}
            detail['status'] = STATUS_CODE["errparam"]
            logger.info(detail)
            return Response(detail)

        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            detail = {'detail': 'Failed to get user profile'}
            detail['status'] = STATUS_CODE["user_no_profile"]
            return Response(detail)

        old_password = base64.b64decode(old_password).decode("utf-8")
        if md5Encode(old_password) != up.payment_password:
            detail = {'detail': 'The old password is not correct.'}
            detail['status'] = STATUS_CODE["pay_passwd_err"]
            logger.error(detail)
            return Response(detail)
        try:
            new_password = base64.b64decode(new_password).decode("utf-8")
            up.payment_password = md5Encode(new_password)
            up.save()
        except Exception as ex:
            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            return Response(detail)

        logger.info('User[%s]\'s payment password changed.')
        detail = {'detail': 'Successfully updated the payment password'}
        detail['status'] = STATUS_CODE["success"]
        return Response(detail)        
                