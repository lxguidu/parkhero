import os
import mimetypes
import hashlib
from datetime import datetime, timedelta
import pytz

from django.http import HttpResponse
#from django.core.servers.basehttp import FileWrapper
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import (
    F, Avg, Count, DecimalField, DurationField, FloatField, Func, IntegerField,
    Max, Min, Sum, Value,
)

from django.db import IntegrityError

from collections import OrderedDict

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser

from userprofile.models import UserProfile, BankCard, Vehicle, Comments
from userprofile.serializers import UserProfileSerializer, VehicleSerializer, BankCardSerializer
from parking.models import ParkingLot
from billing.views import get_vehicle_in_record
from billing.models import OfflinePayment
from billing.serializers import OfflinePaymentSerializer
from parking.models import ParkingLot, VehicleIn, VehicleOut
from parking.serializers import VehicleInSerializer, VehicleOutSerializer

from django.utils.datastructures import MultiValueDictKeyError

from parkhero.status_code import STATUS_CODE
from parkhero.settings import MEDIA_ROOT

import logging
logger = logging.getLogger(__name__)

RESULTS     = 40
MAX_RESULTS = 100
QUERY_DAYS = 7

# Create your views here.

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def userprofile_api(request):
    """
    app api
    """
    if request.method == 'GET':

        if not request.user.is_authenticated():
            error_detail = {"detail":
                            "Authentication credentials were not provided."}
            return Response(error_detail, status=status.HTTP_401_UNAUTHORIZED)
        try:
            #users = UserProfile.objects.all()
            #serializer = UserProfileSerializer(users, many=True)
            #data = serializer.data

            logger.info('user[%s] logged in.' % request.user)

            user = User.objects.get(username=request.user)
            userprofile = UserProfile.objects.get(user=user)
            bankcard = BankCard.objects.filter(owner=user)
            vehicle = Vehicle.objects.filter(owner=user)

            vehicle_serializer = VehicleSerializer(vehicle, many=True)
            v_data = vehicle_serializer.data
            for v in v_data:
                    #pr = ParkingRecord.objects.filter(plate_number=v['plate_number']).latest('created_time')
                pr = get_vehicle_in_record(v['plate_number'])
                if pr:
                    lot = ParkingLot.objects.get(pk=pr.parking_lot_id)
                    parking_lot = lot.name
                    parking_space = ''#pr.parking_space.number
                    parking_time = pr.in_time
                else:
                    parking_lot = ''
                    parking_space = ''
                    parking_time = ''

                v['locked'] = False
                v['parking_lot'] = parking_lot
                v['parking_space'] = parking_space
                v['parking_time'] = parking_time

            response_dict = OrderedDict()
            response_dict['kind'] = 'user#base_info'
            response_dict['avatar'] = userprofile.avatar
            response_dict['phone_number'] = user.username
            response_dict['id_card_number'] = userprofile.id_card_number
            response_dict['nick_name'] = userprofile.nick_name
            response_dict['email'] = user.email
            response_dict['account_balance'] = userprofile.account_balance
            response_dict['vehicles'] = v_data
            response_dict['bank_cards'] = BankCardSerializer(bankcard, many=True).data
            response_dict['status'] = STATUS_CODE["success"]
            logger.info(response_dict)

            return Response(response_dict)

        except UserProfile.DoesNotExist:
            error_detail = {"detail":
                            "The phone number is NOT registed."}
            return Response(error_detail, status=STATUS_CODE["user_no_profile"])

    elif request.method == 'POST':
        logger.info('user[%s] logged in.' % request.user)
        user = User.objects.get(username=request.user)
        try:
            userprofile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            error_detail = {"detail": "The user has not userprofile."}
            return Response(error_detail, status=STATUS_CODE['user_no_profile'])
        try:
            reqdata = request.query_params
            nickname = reqdata.get("nickname")

        except KeyError as ex:
            detail = {"detail": repr(ex)}
            detail['status'] = STATUS_CODE["errparam"]             
            return Response(detail)

        try:
            userprofile.nick_name = nickname
            userprofile.save()

            detail = {'detail': 'Successfully modified user profile.'}
            detail['status'] = STATUS_CODE["success"]
            return Response(detail)
        except (IntegrityError, Exception) as ex:
            detail = {'detail': 'Database error occur, exception: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            logger.warning(detail)
            return Response(detail)            


class FileUploadView(APIView):
    #parser_classes = (FileUploadParser, JSONParser, MultiPartParser, FormParser,)
    parser_classes = (JSONParser, MultiPartParser, FormParser,)
    def post(self, request, format='jpg'):
        print("111111111111111111")
        logger.info(request.user)
        print(request.user)
        if not request.user.is_authenticated():
            print("1111111111111111112")
            error_detail = {"detail": "Authentication credentials were not provided."}
            print(error_detail)            
            return Response(error_detail, status=status.HTTP_401_UNAUTHORIZED)

        print("111111111111111113")
        print("accepted_media_type:%s, content_type: %s, data: %s"%(request.accepted_media_type, request.content_type, request.data))
        print("data: %s"%(request.data))
        
        print("111111111111111113.1")        
        try:
            up_file = request.FILES['filename']
        except (KeyError, MultiValueDictKeyError) as ex:
            key = ex.args[0]
            error_msg = ('Please provide a valid %s.' % key)
            logger.error(error_msg)

            detail = {'detail': error_msg}
            detail['status'] = STATUS_CODE['lostparam']
            #response.data = detail
            #return response
            return Response(detail)

        m, ext = os.path.splitext(up_file.name)
        print("111111111111111113.1_1")
        
        filename = str(request.user) + ext
        print("111111111111111113.1_2")        
        filepath = os.path.join(MEDIA_ROOT, filename)

        print(filepath)

        print("111111111111111113.2")
        destination = open(filepath, 'wb+')
        for chunk in up_file.chunks():
            destination.write(chunk)

        destination.close()
        print("111111111111111113.3")
        md5 = CalcMD5(filepath)
        filedst = os.path.join(MEDIA_ROOT, md5 + filename)

        os.rename(filepath, filedst)
        print("111111111111111114")
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            error_detail = {"detail": "The phone number is NOT registed."}
            return Response(error_detail, status=status.HTTP_406_NOT_ACCEPTABLE)

        print("111111111111111115")
        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            error_detail = {"detail": "The user profile NOT found."}
            return Response(error_detail, status=status.HTTP_406_NOT_ACCEPTABLE)

        up.avatar = md5 + filename
        up.save()
        print("111111111111111116")
        return Response(up_file.name, status.HTTP_201_CREATED)

@api_view(['GET'])
def file_download_api(request):
    if request.method == 'GET':
        filename = request.GET.get('filename')         
          
        if not filename:
            error_msg = ('Please provide a file name.')
            response = Response()
            response.data = {'error_detail': error_msg}
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            logger.error(error_msg)
            return response
    
        filepath = os.path.join(MEDIA_ROOT, filename)

        print(filepath)
        try:
            wrapper = FileWrapper(open(filepath, 'rb'))
            content_length = os.path.getsize(filepath)            
            #wrapper = FileWrapper(open(filepath, 'rb'))
            content_type = mimetypes.guess_type(filepath)[0]
            response = HttpResponse(wrapper, content_type=content_type)               
            response['Content-Length'] = content_length
            logger.info(os.path.getsize(filepath))
            response['Content-Disposition'] = "attachment; filename=%s" %filename
            return response
        except FileNotFoundError as e:
            error_msg = ('No such file or directory: %s' % filename)
            response.data = {'error_detail': error_msg}
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            logger.error(error_msg)
            return response


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def vehicle_in_api(request):    
    plate_number = request.GET.get('plate_number')
    start_index = request.GET.get('start_index')
    max_results = request.GET.get('max_results')
    user = request.user

    detail = 'Please provide a valid plate number.'

    if not plate_number:
        logger.error(detail)
        return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

    try:        
        vehicles = Vehicle.objects.filter(owner=user).filter(plate_number=plate_number)
    except Vehicle.DoesNotExist:
        logger.error(detail)
        return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)        

    if not vehicles.exists():
        logger.error(detail)
        return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

    m = RESULTS
    v_ins = None

    if max_results:
        m = int(max_results)
        if m > MAX_RESULTS:
            m = MAX_RESULTS
        if m < 0:
            m = RESULTS

    now = datetime.now(pytz.utc)    
    before = now + timedelta(days=-QUERY_DAYS)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')

    # only match last 6 digits/characters
    #plate_number = plate_number[-6:]

    try:
        start = int(start_index)
        if start < 0:
            start = 0

        #end = start + m
        if start > 0:                
            v_ins_all = VehicleIn.objects.filter(plate_number__startswith=plate_number).filter(in_time__gt=before_str).filter(id__lt=start).order_by('-in_time')[0:m]
        else:
            v_ins_all = VehicleIn.objects.filter(plate_number__startswith=plate_number).filter(in_time__gt=before_str).order_by('-in_time')[0:m]

    except VehicleIn.DoesNotExist:
        logger.error('Can not find vehicle-in records.')

    if not v_ins_all.exists():
        response_dict = OrderedDict()
        response_dict['kind'] = 'user#vehicle_in'
        response_dict['records'] = []#{'detail': 'No vehicle-in record.'}

        return Response(response_dict)

    serializer = VehicleInSerializer(v_ins_all,many=True)
    data = serializer.data
    parking_lot_ids = list(set([i['parking_lot'] for i in serializer.data]))
    #for i in data:
    try:
        #lot = ParkingLot.objects.get(id=i['parking_lot'])
        parkinglots = ParkingLot.objects.filter(id__in = parking_lot_ids)
        lots_id2name = {i.id: i.name for i in parkinglots}
        for i in data:
            i['id'] = i['parking_lot'] 
            i['parking_lot'] = lots_id2name[i['parking_lot']]
    except ParkingLot.DoesNotExist:
        logger.error('Can not find parking lot has id[%d' % i.parking_lot)
        for i in data:
            i['id'] = i['parking_lot']
            i['parking_lot'] = ''
        #i['parking_lot'] = ''

    response_dict = OrderedDict()
    response_dict['kind'] = 'user#vehicle_in'
    response_dict['records'] = data

    return Response(response_dict)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def vehicle_out_api(request):    
    plate_number = request.GET.get('plate_number')
    start_index = request.GET.get('start_index')
    max_results = request.GET.get('max_results')
    user = request.user

    detail = 'Please provide a valid plate number.'

    if not plate_number:
        return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

    try:
        #vehicle = Vehicle.objects.get(plate_number=plate_number)
        #vehicles = Vehicle.objects.filter(owner=user)
        vehicles = Vehicle.objects.filter(owner=user).filter(plate_number=plate_number)
    except Vehicle.DoesNotExist:
        return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)        

    if not vehicles.exists():
        return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

    m = RESULTS
    v_outs = None

    if max_results:
        m = int(max_results)
        if m > MAX_RESULTS:
            m = MAX_RESULTS
        if m < 0:
            m = RESULTS

    now = datetime.now(pytz.utc)
    #before = datetime(now.year,now.month,now.day-QUERY_DAYS)
    before = now + timedelta(days=-QUERY_DAYS)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')

    # only match last 6 digits/characters
    logger.info(plate_number)
    #plate_number = plate_number[-6:]

    try:
        start = int(start_index)
        if start < 0:
            start = 0
        
        #v_outs_all = VehicleOut.objects.filter(plate_number__contains=plate_number).filter(out_time__gt=before_str).order_by('-out_time')
        if start > 0:            
            v_outs_all = VehicleOut.objects.filter(plate_number__startswith=plate_number).filter(out_time__gt=before_str).filter(id__lt=start).order_by('-out_time')[0:m]
        else:
            v_outs_all = VehicleOut.objects.filter(plate_number__startswith=plate_number).filter(out_time__gt=before_str).order_by('-out_time')[0:m]               

    except VehicleOut.DoesNotExist:
        logger.error('Can not find vehicle-out records.')

    if not v_outs_all.exists():
        data = []#{'detail': 'No vehicle-out record.'}
        response_dict = OrderedDict()
        response_dict['kind'] = 'user#vehicle_out'
        response_dict['records'] = data
        return Response(response_dict)
    
    serializer = VehicleOutSerializer(v_outs,many=True)
    data = serializer.data
    parking_lot_ids = list(set([i['parking_lot'] for i in serializer.data]))    
    try:
        #lot = ParkingLot.objects.get(id=i['parking_lot'])
        parkinglots = ParkingLot.objects.filter(id__in = parking_lot_ids)
        lots_id2name = {i.id: i.name for i in parkinglots}
        for i in data:
            i['id'] = i['parking_lot']
            i['parking_lot'] = lots_id2name[i['parking_lot']]
    except ParkingLot.DoesNotExist:
        logger.error('Can not find parking lot has id[%d' % i.parking_lot)
        for i in data:
            i['id'] = i['parking_lot']
            i['parking_lot'] = ''    

    response_dict = OrderedDict()
    response_dict['kind'] = 'user#vehicle_out'
    response_dict['records'] = data

    return Response(response_dict)    

@api_view(['DELETE', 'GET', 'POST', 'PUT'])
@permission_classes((IsAuthenticated,))
def plate_number_api(request):
    """
    app api
    """
    parser = JSONParser
    confirmed = 'no'
    data = request.data
    user = request.user
    #user = User.objects.get(username='13434491627')

    if request.method == 'DELETE':
        plate_number = data.get('plate_number')

        # android version <= 4.4
        if not plate_number:
            plate_number = request.GET.get('plate_number')
            logger.info('plate number[%s]' % plate_number)

        if not plate_number:
            detail = 'Please provide a plate number.'
            logger.error(detail)
            return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

        # get vehicle record
        try:
            vehicle = Vehicle.objects.get(plate_number=plate_number)
        except Vehicle.DoesNotExist:
            error_detail = ('There is no vehicle with plate number[%s]' % plate_number)
            logger.error(error_detail)
            return Response({'error_detail': error_detail},status=status.HTTP_406_NOT_ACCEPTABLE)

        vehicle.owner.remove(user)
        logger.info('Removed owner[%s] from vehicle[%s]' % (user.username, plate_number))

        return Response({"success": "Successfully deleted the plate number"})

    elif request.method == 'GET':
        try:
            vehicles = Vehicle.objects.filter(owner=user)
        except Vehicle.DoesNotExist:
            logger.error(error_detail)
            return Response({'error_detail': error_detail},status=status.HTTP_406_NOT_ACCEPTABLE)

        logger.info('User[%s] has vehicles[%s]' % (user.username, vehicles))

        response_dict = OrderedDict()
        response_dict['kind'] = 'user#vehicle_info'
        response_dict['vehicles'] = VehicleSerializer(vehicles, many=True).data

        return Response(response_dict)

    elif request.method == 'POST':
        plate_number = data.get('plate_number')
        if plate_number:
            vehicle = Vehicle.objects.get_or_create(plate_number=plate_number)[0]
            vehicle.owner.add(user)
            vehicle.save()

            logger.info('Added vehicle[%s] for [%s].' % (plate_number, user.username))
            return Response({"success": "Successfully added the plate number"})
        else:
            detail = 'Please provide a plate number.'
            logger.error(detail)
            return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

    elif request.method == 'PUT':
        old_plate_number = data.get('old_plate_number')
        new_plate_number = data.get('new_plate_number')

        if not old_plate_number or not new_plate_number:
            detail = 'Please provide plate numbers.'
            logger.error(detail)
            return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

        # get old vehicle record
        try:
            old_vehicle = Vehicle.objects.get(plate_number=old_plate_number)
        except Vehicle.DoesNotExist:
            error_detail = ('There is no vehicle with plate number[%s]' % old_plate_number)
            logger.error('There is no vehicle with plate number[%s]' % old_plate_number)
            return Response({'error_detail': error_detail},status=status.HTTP_406_NOT_ACCEPTABLE)

        # get/create new vehicle record
        new_vehicle = Vehicle.objects.get_or_create(plate_number=new_plate_number)[0]
        old_vehicle.owner.remove(user)
        new_vehicle.owner.add(user)

        old_vehicle.save()
        new_vehicle.save()

        return Response({"success": "Successfully updated the plate number"})

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def comment_api(request):
    parser = JSONParser
    confirmed = 'no'
    data = request.data
    user = request.user

    print(data)
    try:
        comments = Comments()
        comments.owner = user
        comments.comments = data.get('comments')
        comments.save()
    except Exception as e:
        print(str(e))
        logger.error('Can not record the comments.')

    return Response({"success": "Successfully posted the comment."})

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def pay_offline_api(request):
    id = request.GET.get('id')
    plate_number = request.GET.get('plate_number')
    start_index = request.GET.get('start_index')
    max_results = request.GET.get('max_results')
    user = request.user

    detail = 'Please provide a valid plate number.'

    if plate_number:
        try:
            vehicle = Vehicle.objects.get(plate_number=plate_number)
            vehicles = Vehicle.objects.filter(owner=user)
        except Vehicle.DoesNotExist:
            return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

    if vehicle not in vehicles:
        return Response({'detail': detail},status=status.HTTP_406_NOT_ACCEPTABLE)

    m = RESULTS
    v_outs = None

    if max_results:
        m = int(max_results)
        if m > MAX_RESULTS:
            m = MAX_RESULTS
        if m < 0:
            m = RESULTS

    now = datetime.now(pytz.utc)
    before = datetime(now.year,now.month,now.day-QUERY_DAYS)
    before_str = before.strftime('%Y-%m-%d %H:%M:%S')

    # only match last 6 digits/characters
    logger.info(plate_number)
    plate_number = plate_number[-6:]

    try:
        payment_all = OfflinePayment.objects.filter(plate_number__contains=plate_number).filter(payment_time__gt=before_str).order_by('-payment_time')
        total = payment_all.count()
        if id:
            payments = OfflinePayment.objects.filter(pk=id)
        elif start_index:
            start = int(start_index)
            if start < 0:
                start = 0

            end = start + m
            payments = payment_all[start:end]
        else:
            payments = payment_all[:m]

    except OfflinePayment.DoesNotExist:
        logger.error('Can not find  offline payment records.')

    if payments:
        serializer = OfflinePaymentSerializer(payments,many=True)
        data = serializer.data
        for i in data:
            try:
                lot = ParkingLot.objects.get(id=i['parking_lot'])
                i['parking_lot'] = lot.name
            except ParkingLot.DoesNotExist:
                logger.error('Can not find parking lot has id[%d' % i.parking_lot)
                i['parking_lot'] = ''
    else:
        data = []#{'detail': 'No vehicle-out record.'}

    response_dict = OrderedDict()
    response_dict['kind'] = 'user#offline_payment'
    response_dict['records'] = data

    return Response(response_dict)

def CalcMD5(filepath):
    with open(filepath,'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        print(hash)
        return hash


