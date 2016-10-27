#-*- coding: utf-8 -*-
import os

from datetime import datetime
import pytz
from pytz import timezone

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser, FormParser

from django.contrib.auth.models import User

from parkhero.settings import PROJ_HOME

# Create your views here.
import logging
logger = logging.getLogger(__name__)

TZ = pytz.timezone('Asia/Shanghai')


@api_view(['POST'])
def file_upload_api(request):
    parser_classes = (JSONParser, MultiPartParser, FormParser,)
    if request.method == 'POST':

        print(request.FILES.keys())
        up_file = request.FILES['file']

        #filename = request.user
        m, ext = os.path.splitext(up_file.name)
        filename = str(request.user) + ext

        
        apkdirbase = os.path.join(PROJ_HOME, 'app_packages')
        filepath = os.path.join(apkdirbase, filename)       
        print(filepath)

        destination = open(filepath, 'wb+')
        for chunk in up_file.chunks():
            destination.write(chunk)
        destination.close()        
        md5 = CalcMD5(filepath)
        filedst = os.path.join(apkdirbase, md5 + filename)
        os.rename(filepath, filedst)

        return Response(up_file.name, status.HTTP_201_CREATED)