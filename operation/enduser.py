#-*- coding: utf-8 -*-
import pytz
import logging

from datetime import datetime

from pytz import timezone
from collections import OrderedDict
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from userprofile.models import UserProfile, Comments
from parkhero.status_code import STATUS_CODE

logger = logging.getLogger(__name__)

@api_view(['GET', ])
def end_user_info_api(request):
    user = request.user

    # fill in response headers
    response = Response()
    response['Access-Control-Allow-Credentials'] = 'true'

    # authenticate
    if not request.user.is_authenticated():        
        detail = {'detail': 'Please login.'}
        detail['status'] = STATUS_CODE['need_login']
        response.data = detail
        return response

    # only operator_end_user are allowed to operate on parking lot objects
    #role_list = get_role_list(user)
    role_list = [ i['name'] for i in user.groups.values()]
    logger.info('Role list[%s]' % role_list)
    if 'operator_end_user' not in role_list:
        logger.error('Please login as operator_end_user.')
        detail = {'detail': 'Please login as operator_end_user.'}
        #response.status_code = status.HTTP_403_FORBIDDEN
        detail['status'] = STATUS_CODE['non_right']
        response.data = detail
        return response

    if request.method == 'GET':
        end_users = []

        try:
            users = UserProfile.objects.all()
            for u in users:
                user = OrderedDict()
                user['phone_number'] = u.user.username
                user['account_balance'] = u.account_balance
                end_users.append(user)

        except UserProfile.DoesNotExist:
            logger.error('No user profile.')

        utc_time = datetime.now(pytz.utc)
        local_time = utc_time.astimezone(TZ)
        local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')

        response_dict = OrderedDict()
        response_dict['kind'] = 'operation#user_info'
        response_dict['users'] = end_users        

        response_dict['update_time'] = local_time_str
        response_dict['status'] = STATUS_CODE['success']
        logger.info('Total users[%d].' % len(response_dict['users']))
        response.data = response_dict
        return response


@api_view(['GET', ])
def end_user_comments_api(request):
    user = request.user

    # fill in response headers
    response = Response()
    response['Access-Control-Allow-Credentials'] = 'true'
    
    # authenticate
    if not request.user.is_authenticated():        
        detail = {'detail': 'Please login.'}
        detail['status'] = STATUS_CODE['need_login']
        response.data = detail
        return response

    # only operator_end_user are allowed to operate on parking lot objects
    #role_list = get_role_list(user)
    role_list = [ i['name'] for i in user.groups.values()]
    logger.info('Role list[%s]' % role_list)
    if 'operator_end_user' not in role_list:
        logger.error('Please login as operator_end_user.')
        #response.data = {'detail': 'Please login as operator_end_user.'}
        #response.status_code = status.HTTP_403_FORBIDDEN
        detail = {'detail': 'Please login as operator_end_user.'}        
        detail['status'] = STATUS_CODE['non_right']
        response.data = detail
        return response

    if request.method == 'GET':
        comments_all = []

        try:
            comments = Comments.objects.all()
            for item in comments:
                created_time_utc = item.created_time
                created_time_local = created_time_utc.astimezone(TZ)
                created_time_str = created_time_local.strftime('%Y-%m-%d %H:%M:%S')

                c = OrderedDict()
                c['user'] = item.owner.username
                c['comments'] = item.comments
                c['created_time'] = created_time_str
                comments_all.append(c)
        except Comments.DoesNotExist:
            logger.error('No comments.')

        utc_time = datetime.now(pytz.utc)
        local_time = utc_time.astimezone(TZ)
        local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')

        response_dict = OrderedDict()
        response_dict['kind'] = 'operation#user_comments'
        response_dict['comments'] = comments_all

        response_dict['update_time'] = local_time_str
        response_dict['status'] = STATUS_CODE['success']
        logger.info('Total comments[%d].' % len(response_dict['comments']))
        response.data = response_dict
        return response
