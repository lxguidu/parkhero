#-*- coding: utf-8 -*-
import base64
import binascii
import logging
from collections import OrderedDict
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group, Permission
from django.db import transaction

import guardian
from guardian.models import UserObjectPermission

from rest_framework import status
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
from userprofile.models import UserProfile
from parking.models import ParkingLot

logger = logging.getLogger(__name__)

# pre-defined roles
ROLES = ['operator_parkinglot', 'operator_group_user', 'operator_bill',
        'operator_end_user', 'operator_app', 'group_user', 'default']

#@api_view(['DELETE', 'GET', 'POST', 'PUT',])
#@permission_classes((IsAuthenticated,))
class Operator(APIView):
    # ret: 0 - success, 1 - cant login, 2 - can login, but no admin
    def auth_check(self, request):
        logger.info("login as user[%s]"%request.user)
        if not request.user.is_authenticated():
            detail = {'detail': 'Please login.'}
            detail['status'] = STATUS_CODE['need_login']            
            return 1, detail

        if str(request.user) != 'sysadmin':
            detail = {'detail': 'Please login as administrator'}
            detail['status'] = STATUS_CODE['non_administrator']
            return 2, detail

        return 0, None

    # remove an operator
    @permission_classes((IsAuthenticated,))
    def delete(self, request, format=None):               
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)

        data = request.data
        staffid = data.get('staffid')

        if not staffid:
            detail = {'detail': 'Please provide the operator account name.'}
            detail['status'] = STATUS_CODE['lostparam']            
            logger.warning(detail)            
            return Response(detail)

        try:
            operator = User.objects.get(pk=staffid)            
            operator.groups.clear()                 
            operator.user_permissions.clear()                       
            oldpark_lots = guardian.shortcuts.get_objects_for_user(operator, "parking.act_analyse_parkinglot")                       
            UserObjectPermission.objects.bulk_remove_perm('act_analyse_parkinglot', operator, oldpark_lots)            
            operator.delete()
            logger.info('Operator account deleted[%s[' % staffid)
            #response.data = {'success': 'successfully deleted operator[%s]' % staffname}
            detail = {'detail': 'successfully deleted operator[%s]' % staffid}
            detail['status'] = STATUS_CODE['success']
            return Response(detail)

        except (User.DoesNotExist, Exception) as ex:
            logger.warning(ex)
            if isinstance(ex, User.DoesNotExist):
                detail = {'detail': 'Please provide a valid operator account name.'}
                detail['status'] = STATUS_CODE['non_such_user']            
                return Response(detail)

            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            return Response(detail)


    def handle_all_operators(self):
        operator_list = []

        try:
            operators = Group.objects.get_by_natural_key(name='default').user_set.values()
            for item in operators:
                logger.info("operator: %s, dir: %s"%(item, dir(item)))
                operator_list.append({
                    'staffid'    : item['id'],
                    'username'  : item['username'],
                    'email'     : item['email'],                    
                    'realname'  : item['last_name'] + ' '+item['first_name'],
                    'last_login': item['last_login'],
                    'date_joined'   : item['date_joined']
                })
        except (Group.DoesNotExist, Exception) as ex:
            if not isinstance(ex, Group.DoesNotExist):                
                detail = {'detail': 'Database error occur: %s.'%ex}
                detail['kind'] = 'operator#base_info'
                detail['operators'] = operator_list
                detail['status'] = STATUS_CODE["database_err"]
                logger.info(detail)
                return detail            

        logger.info(operator_list)        
        detail = OrderedDict()
        detail['kind'] = 'operator#base_info'
        detail['operators'] = operator_list
        detail['detail'] = 'Successfully get all operator.'
        detail['status'] = STATUS_CODE["success"]            
        return detail

    def handle_one_operator(self, userid):
        try:            
            spec_user = User.objects.get(pk=userid)            
            user_groups = spec_user.groups.values()            
            user_perms = spec_user.get_all_permissions()            
            spec_codenames = [i.split('.')[1] for i in user_perms]            
            specperms = Permission.objects.filter(codename__in=spec_codenames)            
            specparklots = guardian.shortcuts.get_objects_for_user(spec_user, "parking.act_analyse_parkinglot")
            ret_parklots = [{'id': lotitem.id, 'name': lotitem.name} for lotitem in specparklots]            
            detail = {
                'staffid'   : spec_user.id,
                'username'  : spec_user.username,
                'email'     : spec_user.email,
                'first_name': spec_user.first_name,
                'last_name' : spec_user.last_name,                    
                'last_login': spec_user.last_login,
                #'groups'    : user_groups,
                'groups'    : [{"groupId": i['id'], "groupname" :i['name']} for i in user_groups],
                'date_joined'   : spec_user.date_joined,            
                #'permissions'   : user_perms,
                'permissions'   : [{'permid': i.id, 'permname': i.codename, 'permdesc': i.name} for i in specperms],
                'authparklot'   : ret_parklots #specparklots.encode('utf-8')
            }
            
        except (User.DoesNotExist, Exception) as ex:
            detail = {'kind':'operator#detail_info'} 
            if isinstance(ex, User.DoesNotExist):
                detail = {'detail': 'No Such user, id: %s.'%userid}
                detail['status'] = STATUS_CODE['non_such_user']                
            else:
                detail = {'detail': 'Database error occur: %s.'%ex}                               
                detail['status'] = STATUS_CODE["database_err"]

            logger.info(detail)
            return detail
        
        detail['detail'] = 'Successfully get operator info.'
        detail['status'] = STATUS_CODE["success"]
        return detail

    # query operators
    @permission_classes((IsAuthenticated,))
    def get(self, request, format=None):
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)
        
        #data = request.data
        #staffid = data.get('staffid')

        staffid = request.query_params.get('staffid')
        if not staffid: # get all
            detail = self.handle_all_operators()
            return Response(detail)            

        # get an operator
        #else:
        detail = self.handle_one_operator(staffid)
        return Response(detail)


    # add an operator
    @permission_classes((IsAuthenticated,))    
    def post(self, request, format=None):
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)

        data = request.data

        staffname = data.get('staffname')
        password = data.get('password')        

        if not staffname:
            detail = {'detail': 'Please provide the operator account name.'}
            detail['status'] = STATUS_CODE['lostparam']            
            logger.warning(detail)            
            return Response(detail)
        
        # check if user name existed
        try:
            operator = User.objects.get(username=staffname)
            detail = {'detail': 'User name already existed.'}
            detail['status'] = STATUS_CODE['username_exists']            
            return Response(detail)
        except (User.DoesNotExist, Exception) as ex:
            if not isinstance(ex, User.DoesNotExist):
                detail = {'detail': 'Database error occur: %s.'%ex}
                detail['status'] = STATUS_CODE["database_err"]
                return Response(detail)   

        try:            
            operator = User()
            operator.username = staffname
            operator.is_staff = True
            operator.is_active = True                
            operator.set_password(password)                
            operator.save()
            defaultgroup = Group.objects.get(name='default')
            operator.groups.add(defaultgroup)                
        except Exception as ex:
            logger.error(ex)
            detail = {'detail': '%s'%ex}
            detail['status'] = STATUS_CODE['database_err']
            return Response(detail)

        detail = {'detail': 'successfully added operator[%s]' % operator.username}        
        detail['status'] = STATUS_CODE['success']
        return Response(detail)

    # update an operator 
    @permission_classes((IsAuthenticated,))   
    def put(self, request, format=None):
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)        
        
        data = request.data
        staffid = data.get('staffid')
        groupIds = data.get('groups')
        #description = data.get('description')
        #parking_lots = data.get('parking_lots')
        #if not parking_lots:
        #    parking_lots = []
        permIds = data.get('perms')
        parklots = data.get('parklots')

        if not staffid:
            detail = {'detail': 'Please provide the operator account name.'}
            detail['status'] = STATUS_CODE['lostparam']            
            logger.warning(detail)            
            return Response(detail)

        # check if user name existed
        try:
            operator = User.objects.get(pk=staffid)
        except (User.DoesNotExist, Exception) as ex:
            if isinstance(ex, User.DoesNotExist):
                detail = {'detail': 'Please provide a valid operator account name.'}
                detail['status'] = STATUS_CODE['non_such_user']            
                return Response(detail)

            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            return Response(detail)            

        if type(groupIds) == list:
            try:                
                operator.groups.clear()
                if groupIds:
                    specgroups = Group.objects.filter(pk__in=groupIds, name__in=ROLES)                
                    for groupitem in specgroups:
                        operator.groups.add(groupitem)

            except (Group.DoesNotExist, Exception) as ex:
                logger.warning(ex)

        if type(permIds) == list:
            try:
                operator.user_permissions.clear()
                if permIds:                
                    specperms = Permission.objects.filter(pk__in=permIds)                
                    for permitem in specperms:
                        operator.user_permissions.add(permitem)

            except (Permission.DoesNotExist, Exception) as ex:
                logger.warning(ex)
        

        # update parking lot list
        if type(parklots) == list:
            try:
                oldpark_lots = guardian.shortcuts.get_objects_for_user(operator, "parking.act_analyse_parkinglot")
                UserObjectPermission.objects.bulk_remove_perm('act_analyse_parkinglot', operator, oldpark_lots)
                if parklots:
                    park_lots = ParkingLot.objects.filter(id__in=parklots)
                    UserObjectPermission.objects.bulk_assign_perm('act_analyse_parkinglot', operator, park_lots)
                                    
            except (ParkingLot.DoesNotExist, Exception) as ex:                
                logger.warning(ex)                
            
        detail = {'detail': 'successfully updated operator[%s]' % operator.username}
        detail['status'] = STATUS_CODE['success']        
        return Response(detail)