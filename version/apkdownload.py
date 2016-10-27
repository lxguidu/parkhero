import os
import mimetypes
import logging

from django.http import HttpResponse
from wsgiref.util import FileWrapper

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from version.models import AndroidAppVersion
from parkhero.status_code import STATUS_CODE
from parkhero.settings import MEDIA_ROOT

logger = logging.getLogger(__name__)

@api_view(['GET'])
def download_api(request):
    try:
        version = AndroidAppVersion.objects.latest('updated_time')
    except AndroidAppVersion.DoesNotExist:
        detail = {'detail': 'There is NO app package uploaded.'}
        detail['status'] = STATUS_CODE['non_app_release']
        return Response(detail)

    #file_name = version.package_name
    packagename = version.package_name
    file_name = packagename.split('.')[0] + str(version.version_code) + '.' + packagename.split('.')[1]
    file_path = os.path.join(MEDIA_ROOT, file_name)

    logger.info(file_path)

    try:
        wrapper = FileWrapper(open(file_path, 'rb'))
    except (FileNotFoundError, IsADirectoryError) as ex:
        #detail = ('No such file or directory: %s, ex: %s' % (file_name, ex))
        detail = {'detail': 'No such file or directory: %s, ex: %s' % (file_name, ex)}
        detail['status'] = STATUS_CODE['non_file_exists']
        #response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        logger.error(detail)
        return Response(detail)

    content_type = mimetypes.guess_type(file_path)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" %file_name
    return response