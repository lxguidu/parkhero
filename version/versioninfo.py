#-*- coding: utf-8 -*-

import logging

from collections import OrderedDict

from rest_framework.decorators import api_view
from rest_framework.response import Response

from parkhero.status_code import STATUS_CODE
from version.models import AndroidAppVersion

logger = logging.getLogger(__name__)

# Create your views here.
@api_view(['GET'])
def version_info_api(request):
    try:
        version = AndroidAppVersion.objects.latest('updated_time')
    except AndroidAppVersion.DoesNotExist:
        detail = {'detail': 'The is NO app released.'}
        detail['status'] = STATUS_CODE['non_app_release']
        return Response(detail)

    detail = {}
    detail['kind'] = 'operation#app_version'
    detail['version_code'] = version.version_code
    detail['version_name'] = version.version_name
    detail['package_name'] = version.package_name
    detail['release_date'] = version.release_date
    detail['release_notes'] = version.release_notes
    detail['status'] = STATUS_CODE['success']

    logger.info(detail)

    return Response(detail)