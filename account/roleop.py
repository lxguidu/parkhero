#-*- coding: utf-8 -*-
import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group, Permission

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


logger = logging.getLogger(__name__)

# pre-defined roles
ROLES = ['operator_parkinglot', 'operator_group_user', 'operator_bill',
        'operator_end_user', 'operator_app', 'group_user', 'default']

# 角色的增删改查，改主要是针对权限，并且是模块级的权限，而不是对象级别的，
# 因为对象级别的需求(group_user)在operator里面已经进行了处理，其它需求的
# 级别都是模块级，所以此处只进行模块级的处理

class Role_Op(APIView):
    # ret: 0 - success, 1 - cant login, 2 - can login, but no admin
    def auth_check(self, request):
        if not request.user.is_authenticated():
            detail = {'detail': 'Please login.'}
            detail['status'] = STATUS_CODE['need_login']            
            return 1, detail

        if str(request.user) != 'sysadmin':
            detail = {'detail': 'Please login as administrator'}
            detail['status'] = STATUS_CODE['non_administrator']
            return 2, detail

        return 0, None

    # remove an role
    @permission_classes((IsAuthenticated,))
    def delete(self, request, format=None):   
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)

        data = request.data
        groupId = data.get('groupId')

        if not groupId:
            detail = {'detail': 'Please provide the group id.'}
            detail['status'] = STATUS_CODE['lostparam']
            logger.warning(detail)
            return Response(detail)

        try:
            specgroup = Group.objects.get(pk=groupId, name__in=ROLES)
            specgroup.permissions.clear()
            specgroup.delete()
            detail = {'detail': 'successfully deleted group[%s]' % specgroup.name}
            detail['status'] = STATUS_CODE['success']
            return Response(detail)
        except (Group.DoesNotExist, Exception) as ex:
            if isinstance(ex, Group.DoesNotExist):
                detail = {'detail': 'Please provide a valid group id[%s].'%groupId}
                detail['status'] = STATUS_CODE['non_such_role']
                logger.warning(detail)            
                return Response(detail)

            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            logger.warning(detail) 
            return Response(detail)

    # query role
    @permission_classes((IsAuthenticated,))
    def get(self, request, format=None):
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)
        
        data = request.data
        groupId = data.get('groupId')
        if not groupId: # get all
            try:
                allgroups = Group.objects.all()
                groupinfo = []
                for item in allgroups:
                    if item.name in ROLES:
                        groupinfo.append({
                            "groupId"   :item.id,
                            "groupname" :item.name
                        })
                detail = {'detail': 'successfully get all group info'}
                detail['status'] = STATUS_CODE['success']   
                detail['groupinfo'] = groupinfo             
                return Response(detail)
            except Exception as ex:
                detail = {'detail': 'Database error occur: %s.'%ex}
                detail['status'] = STATUS_CODE["database_err"]
                logger.warning(detail) 
                return Response(detail)            
        try:
            #detail = self.handle_one_group(groupid)
            specgroup = Group.objects.get(pk=groupId)
            specperms = specgroup.permissions.values()
            perminfos = []
            for permitem in specperms:
                perminfos.append({
                    'permid'    : permitem.id,
                    'permname'  : permitem.codename,
                    'permdesc'  : permitem.name                    
                })
            
            detail = {'detail': 'successfully get group[%s]\' info'%groupid}
            detail['perminfo'] = perminfos
            detail['status'] = STATUS_CODE['success']
            return Response(detail)
        except (Group.DoesNotExist, Exception) as ex:
            if isinstance(ex, Group.DoesNotExist):
                detail = {'detail': 'No Such group: %s.'%ex}
                detail['status'] = STATUS_CODE["non_such_role"]
                logger.warning(detail) 
                return Response(detail)

            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            logger.warning(detail) 
            return Response(detail)
        


    # add an role
    @permission_classes((IsAuthenticated,))    
    def post(self, request, format=None):
        retval, ret_detail = self.auth_check(request)
        if retval != 0:            
            return Response(ret_detail)

        data = request.data

        groupname = data.get('groupname')                

        if not groupname or groupname not in ROLES:
            detail = {'detail': 'Please provide a valid group name.'}
            detail['status'] = STATUS_CODE['lostparam']            
            logger.warning(detail)            
            return Response(detail)
        
        # check if user name existed
        try:
            specgroup = Group.objects.get(name=groupname)
            detail = {'detail': 'Group name already existed.'}
            detail['status'] = STATUS_CODE['groupname_exists']            
            return Response(detail)
        except (Group.DoesNotExist, Exception) as ex:
            if not isinstance(ex, Group.DoesNotExist):
                detail = {'detail': 'Database error occur: %s.'%ex}
                detail['status'] = STATUS_CODE["database_err"]
                return Response(detail)   

        try:            
            newgroup = Group()
            newgroup.name = groupname                            
            newgroup.save()             
        except Exception as ex:
            logger.error(ex)
            detail = {'detail': '%s'%ex}
            detail['status'] = STATUS_CODE['database_err']
            return Response(detail)

        detail = {'detail': 'successfully added group[%s]' % groupname}        
        detail['status'] = STATUS_CODE['success']
        return Response(detail)
        pass


    # update an role 
    @permission_classes((IsAuthenticated,))   
    def put(self, request, format=None):
        data = request.data
        groupId = data.get('groupId')        
        permIds = data.get('perms')
        if permIds[0] == '[':
            permIds = permIds[1:len(permIds)-1]
            
        permIds = permIds.split(',')        
        print("groupId: %s"%groupId)
        print("permIds: %s"%permIds)
        if not groupId or not permIds:
            detail = {'detail': 'Please provide a valid param.'}
            detail['status'] = STATUS_CODE['lostparam']            
            logger.warning(detail)            
            return Response(detail)
        
        try:
            specgroup = Group.objects.get(pk=groupId)

            for permitem in permIds:
                specgroup.permissions.add(permitem)

            detail = {'detail': 'successfully change group[%s]' % groupId}        
            detail['status'] = STATUS_CODE['success']
            return Response(detail)

        except (Group.DoesNotExist, Exception) as ex:
            if isinstance(ex, Group.DoesNotExist):
                detail = {'detail': 'No Such group: %s.'%ex}
                detail['status'] = STATUS_CODE["non_such_role"]
                logger.warning(detail)                
                return Response(detail)

            detail = {'detail': 'Database error occur: %s.'%ex}
            detail['status'] = STATUS_CODE["database_err"]
            logger.warning(detail) 
            return Response(detail)