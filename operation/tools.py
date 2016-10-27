#-*- coding: utf-8 -*-
from subprocess import call

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User

from parking.models import ParkingLot
from parkhero.status_code import STATUS_CODE

# from userprofile.models import ParkingLotGroup

# Create your views here.
import logging
logger = logging.getLogger(__name__)

PRIVATE_KEY_SUFFIX = '_pri_key.pem'
PRIVATE_KEY_PKCS8_SUFFIX = '_pri_key_pkcs8.pem'
PUBLIC_KEY_SUFFIX = '_pub_key.pem'

def get_parking_lots(user):
    parking_lots = []
    try:
        groups = user.parkinglotgroup_set.all()
        for g in groups:
            lots = g.parking_lot.all()
            for l in lots:
                parking_lots.append(l)
    except ParkingLotGroup.DoesNotExist:
        pass
    except ParkingLot.DoesNotExist:
        pass

    return parking_lots

def generate_key(key_name):
    # name of the keys
    pri_key_name = key_name + PRIVATE_KEY_SUFFIX
    pri_key_pkcs8_name = key_name + PRIVATE_KEY_PKCS8_SUFFIX
    pub_key_name = key_name + PUBLIC_KEY_SUFFIX

    # private key
    call(['openssl', 'genrsa', '-out', pri_key_name, '1024'])

    # private key in pkcs8
    call(['openssl', 'pkcs8', '-topk8',
          '-in', pri_key_name,
          '-out', pri_key_pkcs8_name,
          '-nocrypt'])

    # public key
    call(['openssl', 'rsa',
          '-in', pri_key_name,
          '-RSAPublicKey_out',
          '-out', pub_key_name])

def login_check(request):
    logger.info("login as user[%s]"%request.user)
    if not request.user.is_authenticated():
        detail = {'detail': 'Please login.'}
        detail['status'] = STATUS_CODE['need_login']            
        return 1, detail
    return 0, None

def group_check(user, groupname):
    # only spec group are allowed to operate on parking lot objects    
    role_list = [ i['name'] for i in user.groups.values()]
    logger.info('Role list[%s]' % role_list)        
    if groupname not in role_list:
        logger.error('Please login as %s.'%groupname)
        detail = {'detail': 'Please login as %s.'%groupname}            
        detail['status'] = STATUS_CODE['non_right']
        return 1, detail

    return 0, role_list

def auth_check(request, groupname):
    retval, ret_detail = login_check(request)
    if retval != 0:
        return 1, ret_detail

    retval, ret_detail = group_check(request.user, groupname)
    if retval != 0:
        return 2, ret_detail         

    return 0, ret_detail # role_list