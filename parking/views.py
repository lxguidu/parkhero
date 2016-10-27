import os
import mimetypes
import json
import pytz
import time
import hashlib

from collections import OrderedDict
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

from django.shortcuts import render
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from userprofile.models import UserProfile, Vehicle
from parking.models import (
    ParkingLot, ParkingSpace, VehicleIn, VehicleOut,
    RoadsideParkingRegister,
)
from parking.serializers import ParkingLotSerializer, ParkingSpaceSerializer
from parkhero.settings import MEDIA_ROOT

import logging
logger = logging.getLogger(__name__)
#tz = pytz.timezone('Asia/Shanghai')

# Create your views here.
def parkinglot(request):

    context_dict = {}

    try:
        lots = ParkingLot.objects.all()
        for l in lots:
            s = ParkingSpace.objects.filter(parking_lot=l)
            l.space_total = len(s)
            s = ParkingSpace.objects.filter(parking_lot=l, status='A')
            l.space_available = len(s)

        context_dict['lots'] = lots

    except ParkingLot.DoesNotExist:
        pass

    return render(request, 'parking/parkinglot.html', context_dict)

def parkingspace(request, parking_lot_id):

    context_dict = {}

    try:
        spaces = ParkingSpace.objects.filter(parking_lot=parking_lot_id)

        context_dict['spaces'] = spaces
    except ParkingSpace.DoesNotExist:
        pass

    return render(request, 'parking/parkingspace.html', context_dict)

@api_view(['GET', 'POST'])
def parkinglot_api(request):
    """
    app api
    """
    if request.method == 'GET':
        try:
            city_code = request.GET.get('city_code')
            id = request.GET.get('id')
            longitude = request.GET.get('longitude')
            latitude = request.GET.get('latitude')
            distance = request.GET.get('distance')
            start_index = request.GET.get('start_index')
            max_results = request.GET.get('max_results')
            name = request.GET.get('name')

            if id:
                print('Get parking lots by id.')
                lots = ParkingLot.objects.filter(pk=id)
            elif city_code:
                print('Get parking lots by city code.')
                lots = ParkingLot.objects.filter(city_code=city_code)
            elif name:
                logger.info('Get parking lots by name[%s].' % name)
                lots = ParkingLot.objects.filter(name__contains=name)
            elif longitude and latitude and distance:
                print('Get parking lots by position and distance.')
                d_lots = ParkingLot.objects.all()
                lots = []
                for l in d_lots:
                    dist = get_distance(l.longitude,l.latitude,float(longitude),float(latitude))

                    # max distance is 3 kilometer
                    max_distance = float(distance)
                    if max_distance > 3:
                         max_distance = 3

                    if dist <= max_distance:
                        print('parking lot[%s], distance[%f]' % (l.name,dist))
                        l.distance = dist
                        lots.append(l)
            else:
                print('Get all parking lots.')
                lots = ParkingLot.objects.filter(is_active=True)

            if start_index:
                start = int(start_index)
            else:
                start = 0


            if max_results:
                m = int(max_results)
                if m > 40:
                    m = 40
                end = start + m
            else:
                end = start + 10

            lots_data = lots[start:end]
            # update parking space info
            for l in lots_data:
                a,t = get_parking_space_info(l.id)
                #print('avail[%d], total[%d]' % (a,t))
                # get real time info from vehicle in/out record
                if t != 0:
                    #if a < 0:
                    #    a = 0
                    l.parking_space_available = a
                    #l.parking_space_total = t

            response_dict = OrderedDict()
            response_dict['kind'] = 'parking_lots#nearby'
            #ponse_dict['parking_lots'] = ParkingLotSerializer(lots[start:end], many=True).data
            data_mod = ParkingLotSerializer(lots_data, many=True).data
            for i in data_mod:
                if i['parking_space_available'] < 0:                    
                    logger.info("parking lot[%s]-%s, parking_space_available: %s"%(i['id'], i['name'], i['parking_space_available']))
                    i['parking_space_available'] = 0

            #response_dict['parking_lots'] = ParkingLotSerializer(lots_data, many=True).data
            response_dict['parking_lots'] = data_mod
            

            response_dict['update_time'] = datetime.now().replace(tzinfo=pytz.utc)
            #print(response_dict)
            logger.info('Total parking lots[%d].' % len(response_dict['parking_lots']))            

            response = Response(response_dict)            
            return response
            

        except ParkingLot.DoesNotExist:
            error_detail = {"detail":
                            "The is NO parking lot."}
            return Response(error_detail, status=status.HTTP_404_NOT_FOUND)
            pass

    elif request.method == 'POST':
        pass


@api_view(['GET'])
def parking_lot_image_api(request):
    """
    app api
    """
    response = Response()

    if request.method == 'GET':
        file_name = request.GET.get('filename')
        if not file_name:
            error_msg = ('Please provide a filename.')
            response.data = {'error_detail': error_msg}
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            logger.error(error_msg)
            return response
 
        file_path = os.path.join(MEDIA_ROOT, file_name)

        logger.info(file_path)

        try:
            wrapper = FileWrapper(open(file_path, 'rb'))
        except FileNotFoundError as e:
            error_msg = ('No such file or directory: %s' % file_name)
            response.data = {'error_detail': error_msg}
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            logger.error(error_msg)
            return response

        content_type = mimetypes.guess_type(file_path)[0]
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(file_path)
        logger.info(os.path.getsize(file_path))
        response['Content-Disposition'] = "attachment; filename=%s" %file_name
        return response

@api_view(['GET', 'POST'])
def parking_api(request):
    """
    app api
    """
    if request.method == 'GET':
        plate_number = request.GET.get('plate_number')
        print(plate_number)

        #return Response(status=200)

        if plate_number:
            try:
                r = ParkingRecord.objects.filter(plate_number=plate_number).latest('created_time')
                if r.type is 'parking':

                    return Response('Got it!')

            except ParkingRecord.DoesNotExist:
                # let's created one
                return Response({"detail": "No record found."}, status=404)

        else:
            return Response({"detail": "Please provide the plate number"})

    elif request.method == 'POST':
        pass

@api_view(['POST'])
def vehicle_in_api(request):
    parser = JSONParser
    confirmed = 'no'
    data = request.data

    try:
        identifier = str(data['identifier'])
        in_time = data['intime']
        in_time = in_time.replace('/','-') # uniform date format
        plate_number = data['carno']
    except KeyError as e:
        error_detail = {"detail": repr(e)}
        print(error_detail)
        return Response(error_detail, status=status.HTTP_406_NOT_ACCEPTABLE)

    # verify the parking lot
    try:
        
        lot = ParkingLot.objects.get(identifier=identifier)
    except ParkingLot.DoesNotExist:        
        return Response({'detail': 'No parking lot named as[%s].' % identifier}, status=404)

    # check duplication
    #notice_id = data['notice_id']

    # upload tool is unable to provide correct notice ids
    # we have to calculate it by ourselves
    # it's the md5 of 'in_time' + 'carno' + 'identifier'
    notice_id = cacl_notice_id(in_time, plate_number, identifier)
    #logger.info(notice_id)

    try:
        v_in = VehicleIn.objects.get(notice_id=notice_id)
        logger.error('Duplicated vehicle-in record[%s][%s][%s][%s][%s].' % (notice_id,lot.name,plate_number,data['timestamp'],in_time))
        return Response('success')
    except VehicleIn.DoesNotExist:
        pass
    except VehicleIn.MultipleObjectsReturned:
        v_ins = VehicleIn.objects.filter(notice_id=notice_id)
        for i in range(0, v_ins.count()-1):
            v_ins[i].delete()
            logger.error('One duplicated vehicle-in record deleted[%s][%s][%s][%s][%s].' % (notice_id,lot.name,plate_number,data['timestamp'],in_time))

        logger.error('Duplicated vehicle-in record[%s][%s][%s][%s][%s].' % (notice_id,lot.name,plate_number,data['timestamp'],in_time))
        return Response('success')

    pr = VehicleIn(parking_lot=lot)

    #print(data)

    try:
        pr.plate_number  = plate_number
        pr.in_time = in_time#datetime.strptime(data['intime'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
        pr.time_stamp = data['timestamp']#datetime.fromtimestamp(int(data['timestamp'])).replace(tzinfo=pytz.utc)
        pr.notice_id = notice_id
        pr.price_list = data['pricelist']
        pr.parking_space_available = data['space_available']
        pr.parking_space_total = data['space_total']
        pr.created_time = datetime.now(pytz.utc)
        #pr.parking_space_id = 1

        pr.save()

        logger.info('space total[%d], space available[%d]' % (data['space_total'],data['space_available']))
        logger.info('inserted vehicle-in record[%s][%s][%s][%s][%s].' % (notice_id,lot.name,plate_number,data['timestamp'],in_time))

    except KeyError as e:
        detail = {"detail": repr(e)}
        logger.error(detail)
        return Response(detail, status=status.HTTP_406_NOT_ACCEPTABLE)


    return Response('success')



@api_view(['POST'])
def vehicle_out_api(request):
    parser = JSONParser
    confirmed = 'no'
    data = request.data

    try:
        identifier = str(data['identifier'])
        out_time = data['outtime']
        out_time = out_time.replace('/','-') # uniform date format
        plate_number = data['carno']
    except KeyError as e:
        error_detail = {'detail': repr(e)}
        print(error_detail)
        return Response(error_detail, status=status.HTTP_406_NOT_ACCEPTABLE)

    # verify the entrance
    try:
        lot = ParkingLot.objects.get(identifier=identifier)
    except ParkingLot.DoesNotExist:        
        return Response({'detail': 'No parking lot named as[%s].' % identifier}, status=404)

    # check duplication
    notice_id = data['notice_id']
    notice_id = cacl_notice_id(out_time, plate_number, identifier)

    try:
        v_out = VehicleOut.objects.get(notice_id=notice_id)
        logger.error('Duplicated vehicle-out record[%s][%s][%s][%s][%s].' % (notice_id,lot.name,plate_number,data['timestamp'],out_time))
        return Response('success')
    except VehicleOut.DoesNotExist:
        pass
    except VehicleOut.MultipleObjectsReturned:
        v_outs = VehicleOut.objects.filter(notice_id=notice_id)
        for i in range(0, v_outs.count()-1):
            v_outs[i].delete()
            logger.error('One duplicated vehicle-out record deleted[%s][%s][%s][%s][%s].' % (notice_id,lot.name,plate_number,data['timestamp'],out_time))

        logger.error('Duplicated vehicle-out record[%s][%s][%s][%s][%s].' % (notice_id,lot.name,plate_number,data['timestamp'],out_time))
        return Response('success')            

    pr = VehicleOut(parking_lot=lot)

    try:
        pr.plate_number  = plate_number
        pr.out_time = out_time#datetime.strptime(data['outtime'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
        pr.time_stamp = data['timestamp']#datetime.fromtimestamp(int(data['timestamp'])).replace(tzinfo=pytz.utc)
        pr.notice_id = notice_id
        pr.parking_space_available = data['space_available']
        pr.parking_space_total = data['space_total']
        pr.created_time = datetime.now(pytz.utc)
        #pr.parking_space_id = 1

        pr.save()

        logger.info('space total[%d], space available[%d]' % (data['space_total'],data['space_available']))
        logger.info('inserted vehicle-out record[%s][%s][%s][%s][%s].' % (notice_id,lot.name,plate_number,data['timestamp'],out_time))

    except KeyError as e:
        detail = {"detail": repr(e)}
        logger.error(detail)
        return Response(detail, status=status.HTTP_406_NOT_ACCEPTABLE)


    return Response('success')


@api_view(['GET'])
def get_private_key_api(request):
    identifier = request.GET.get('identifier')

    if identifier:
        try:
            lot = ParkingLot.objects.get(identifier=identifier)
            print(lot.name)
            pri_key = lot.private_key
            response_dict = OrderedDict()
            response_dict['key'] = pri_key

            return Response(response_dict)

        except ParkingLot.DoesNotExist:
            error_detail = {"detail":
                            "The is NO parking lot[%s]." % identifier}
            return Response(error_detail, status=404)
    else:
        return Response({"detail": "Please provide a valid parking lot identifier."})

@api_view(['GET'])
def get_public_key_api(request):
    identifier = request.GET.get('identifier')

    if identifier:
        try:
            lot = ParkingLot.objects.get(identifier=identifier)
            logger.debug(lot.name)
            pub_key = lot.public_key
            response_dict = OrderedDict()
            response_dict['key'] = pub_key

            return Response(response_dict)

        except ParkingLot.DoesNotExist:
            detail = {"detail":
                            "The is NO parking lot[%s]." % identifier}
            return Response(detail, status=404)
    else:
        return Response({"detail": "Please provide a valid parking lot identifier."})

def get_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

def get_parking_space_info(parking_lot_id):

    space_avail = 0
    space_total = 0
    latest = 0#datetime.fromtimestamp(1453084036).replace(tzinfo=pytz.utc)

    # check vehicle-in records
    try:
        vi = VehicleIn.objects.filter(parking_lot=parking_lot_id).latest('in_time')
            
        try:            
            ts_vi = int(time.mktime(vi.in_time.timetuple()))
        except ValueError as ex:            
            logger.warning(ex)
            
        if ts_vi > latest:
            space_avail = vi.parking_space_available
            space_total = vi.parking_space_total
            latest = ts_vi

    except VehicleIn.DoesNotExist:        
        pass

    # check vehicle-in records
    try:
        vo = VehicleOut.objects.filter(parking_lot=parking_lot_id).latest('out_time')
        
        try:
            ts_vo = int(time.mktime(vo.out_time.timetuple()))
        except ValueError:
            ts_vo = int(time.mktime(vo.out_time.timetuple()))

        if ts_vo > latest:
            space_avail = vo.parking_space_available
            space_total = vo.parking_space_total

    except VehicleOut.DoesNotExist:        
        pass

    return space_avail,space_total

def get_parking_records(user_id):
    # by plate number. get closed parking lot records
    try:
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
        vehicles = Vehicle.objects.filter(owner=user)
    except User.DoesNotExist:
        print('user not found[%d]' % user_id)
    except UserProfile.DoesNotExist:
        print('user profile not found[%d]' % user_id)
    except Vehicle.DoesNotExist:
        print('vehicle not found[%d]' % user_id)

    records = []

    for v in vehicles:
        pn = v.plate_number
        try:
            v_in = VehicleIn.objects.filter(plate_number__endswith=pn[-6:]).latest('in_time')
        except VehicleIn.DoesNotExist:
            continue

        try:
            v_out = VehicleOut.objects.filter(plate_number__endswith=pn[-6:]).latest('out_time')
            diff = v_out.out_time - v_in.in_time
            #if diff < 0:
            if v_in.in_time > v_out.out_time:
                records.append(v_in.id)
        except VehicleOut.DoesNotExist:
            records.append(v_in.id)

    # by user id. get road side parking records
    try:
        rsp = RoadsideParkingRegister.objects.filter(user=user).latest('created_time')
        v_in = VehicleIn.objects.filter(parking_space=rsp.parking_space).latest('in_time')
        v_out = VehicleOut.objects.filter(parking_space=rsp.parking_space).latest('out_time')
        #diff = v_out.out_time - v_in.in_time
        #if diff < 0:
        if v_in.in_time > v_out.out_time:
            records.append(v_in.id)
    except RoadsideParkingRegister.DoesNotExist:
        pass
    except VehicleIn.DoesNotExist:
        pass
    except VehicleOut.DoesNotExist:
        records.append(v_in.id)

    return records

def cacl_notice_id(in_time, carno, identifier):
    input = in_time + carno + identifier
    m = hashlib.md5()
    m.update(input.encode('utf-8'))
    output = m.hexdigest()

    return output

