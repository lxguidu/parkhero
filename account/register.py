#-*- coding: utf-8 -*-
import base64
import logging
from collections import OrderedDict
from datetime import datetime

from django.contrib.auth.models import User, Group, Permission
from django.db import transaction

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
from userprofile.models import UserProfile

from parkhero.status_code import STATUS_CODE

logger = logging.getLogger(__name__)

class Register(APIView):
    def post(self, request, format=None):
        data = request.data

        try:
            phone_number = data['phone_number']    
            #plate_number = data['plate_number']
            verification_code = data['verification_code']            
        except KeyError as ex:
            detail = {"detail": repr(ex)}
            detail['status'] = STATUS_CODE["errparam"]
            logger.warning(detail)        
            return Response(detail)    

        # check verification code
        try:
            vc = VerificationCode.objects.get(phone_number=phone_number)
        except VerificationCode.DoesNotExist:
            detail = {"detail": "Please wait a moment or re-enter verification code."}
            detail['status'] = STATUS_CODE["verify_code_wait"]
            logger.warning(detail)
            return Response(detail)

        time_diff = datetime.now() - vc.created_time.replace(tzinfo=None)
        if int(time_diff.total_seconds()) > 600:
            try:
                vc.delete()
            except Exception as ex:
                logger.warning('Database error occur: %s.'%ex)

            detail = {"detail": "Verification code has expired."}
            detail['status'] = STATUS_CODE["verify_code_expired"]
            return Response(detail)

        if vc.verification_code != verification_code:
            detail = {"detail": "Verification code is invalid."}
            detail['status'] = STATUS_CODE["verify_code_invalid"]
            return Response(detail)           

        # phone number check
        try:            
            user = User.objects.get(username=phone_number)
            detail = {"detail": "The phone number is already registed."}
            detail['status'] = STATUS_CODE["phone_num_registed"]
            return Response(detail)
        except User.DoesNotExist:
            # it's ok
            pass


        try:
            with transaction.atomic():
                user = User()
                user.username = phone_number
                user.is_staff = True
                user.is_active = True
                user.save()

                up = UserProfile.objects.get_or_create(user=user)[0]
                up.account_balance = 1000
                up.save()
                logger.warning("new user[%s] profile created."%phone_number) 
        except Exception as ex:
            detail = {'detail': 'database error: %s occur.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            logger.warning(detail)
            logger.warning(ex)
            return Response(detail)

        detail = {'detail': 'Successfully registered.'}
        detail['status'] = STATUS_CODE["success"]
        return Response(detail)