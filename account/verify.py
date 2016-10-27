#-*- coding: utf-8 -*-
import base64
import logging
import pytz
import random
from collections import OrderedDict
from datetime import datetime

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

from parkhero.status_code import STATUS_CODE
from account.models import VerificationCode

from yuntongxun_sms.CCP_REST_DEMO_Python_v2_7r.DEMO.SendTemplateSMS import sendTemplateSMS

logger = logging.getLogger(__name__)

class Verify(APIView):
    def phone_number_check(self, phonenum):
        ret = False
        error_detail = {}
        # 3 digits prefix
        phoneprefix=['130','131','132','133','134','135','136','137','138','139',
                     '150','151','152','153','155','156','157','158','159',
                     '170','176','177','178',
                     '180','181','182','183','184','185','186','187','188','189']

        # lenth of the number should be 11
        if len(str(phonenum)) != 11:
            error_detail['detail'] = "The length of phone number should be 11."
            return ret, error_detail
        
        if not phonenum.isdigit():
            error_detail['detail'] = "The phone number should all be digits."
            return ret, error_detail

        # check the prefix
        if phonenum[:3] in phoneprefix:
            error_detail['detail'] = "The phone number is valid."
            ret = True
        else:
            error_detail['detail'] = "The phone number is invalid."   

        return ret, error_detail

    def create_verification_code(self):
        chars=['0','1','2','3','4','5','6','7','8','9']
        x = random.choice(chars), random.choice(chars),random.choice(chars), random.choice(chars),random.choice(chars), random.choice(chars)        
        code = "".join(x)
        #print(code)
        logger.info(code)
        return code

    def get(self, request, format=None):
        phone_number = request.GET.get('phone_number')    
        ret, error_msg = self.phone_number_check(phone_number)
        if not ret:
            error_msg["status"] = STATUS_CODE["errparam"]
            logger.warning(error_msg)
            return Response(error_msg)
    
        try:
            p =  VerificationCode.objects.get(phone_number=phone_number)
            p.delete()
        except (VerificationCode.DoesNotExist, Exception) as ex:
            if not isinstance(ex, VerificationCode.DoesNotExist):
                detail = {'detail': 'Database error occur: %s.'%ex}
                detail['status'] = STATUS_CODE["database_err"]
                logger.warning(detail)
                return Response(detail)

        code = self.create_verification_code()
        result = sendTemplateSMS(phone_number, [code, '10'], 52368)

        print(result)
        statusCode = ''
        for k,v in result.items():
            if k == 'statusCode':
                statusCode = v

        if statusCode == '000000':
            try:
                p = VerificationCode()
                p.phone_number = phone_number
                p.verification_code = code
                p.created_time = datetime.now(pytz.utc)
                p.save()
                detail = {"detail": "Successfully sent SMS."}
                detail['status'] = STATUS_CODE["success"]
                return Response(detail)
            except Exception as ex:
                detail = {'detail': 'Database error occur: %s.'%ex}
                detail['status'] = STATUS_CODE["database_err"]
                logger.warning(detail)
                return Response(detail)

        
        logger.info("result sms: %s"%result)
        detail = {'detail': "network error!"}
        detail['status'] = STATUS_CODE["network_err"]
        logger.warning(detail)
        return Response(detail)
        #return Response(result, status=status.HTTP_403_FORBIDDEN)