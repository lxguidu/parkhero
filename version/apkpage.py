import os
import mimetypes
import logging

from wsgiref.util import FileWrapper

from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from parkhero.status_code import STATUS_CODE
from parkhero.settings import MEDIA_ROOT

from version.models import CoverPages, IndexPages, StartupPages

logger = logging.getLogger(__name__)

@api_view(['GET'])
def slide_show_api(request):
    """
    app api
    """   
    if request.method == 'GET':
        try:
            index_pages = IndexPages.objects.all()
            startup_pages = StartupPages.objects.all()
            cover_pages = CoverPages.objects.all()
        except (IndexPages.DoesNotExist):
            index_pages = []
        except (StartupPages.DoesNotExist):
            startup_pages = []
        except (CoverPages.DoesNotExist):
            cover_pages = []

        index_index = []
        startup_index = []
        cover_index = []

        for p in index_pages:
            if p.file_name != '':
                index_index.append(p.index)

        for p in startup_pages:
            if p.file_name != '':
                startup_index.append(p.index)

        for p in cover_pages:
            if p.file_name != '':
                cover_index.append(p.index)

        detail = {}
        detail['kind'] = 'version#slide_show'
        detail['startup_pages'] = startup_index
        detail['index_pages'] = index_index
        detail['cover_pages'] = cover_index
        detail['status'] = STATUS_CODE['success']
        
        return Response(detail)

@api_view(['GET'])
def startup_page_api(request):
    """
    app api
    """
    response = Response()

    if request.method == 'GET':
        index = request.GET.get('index')

        try:
            image = StartupPages.objects.get(index=index)
        except StartupPages.DoesNotExist:                      
            detail = {'detail': 'No startup image.'}
            detail['status'] = STATUS_CODE['non_startup_image']
            logger.error(detail)
            response.data = detail
            return response
        except ValueError:
            detail = {'detail': 'Please provide a valid index.'}
            detail['status'] = STATUS_CODE['errparam']
            logger.error(detail)
            response.data = detail                       
            return response

        file_name = image.file_name
        file_path = os.path.join(MEDIA_ROOT, file_name)

        logger.info(file_path)

        try:
            wrapper = FileWrapper(open(file_path, 'rb'))
        except (FileNotFoundError, IsADirectoryError) as ex:
            detail = {'detail': 'No such file or directory: %s, ex: %s' % (file_name, ex)}
            detail['status'] = STATUS_CODE['non_file_exists']
            logger.error(detail)
            response.data = detail                       
            return response

        content_type = mimetypes.guess_type(file_path)[0]
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(file_path)
        logger.info(os.path.getsize(file_path))
        response['Content-Disposition'] = "attachment; filename=%s" %file_name
        return response

@api_view(['GET'])
def index_page_api(request):
    """
    app api
    """
    response = Response()

    if request.method == 'GET':
        index = request.GET.get('index')

        try:
            image = IndexPages.objects.get(index=index)
        except IndexPages.DoesNotExist:
            detail = {'detail': 'No index image.'}
            detail['status'] = STATUS_CODE['non_index_image']
            logger.error(detail)
            response.data = detail
            return response
        except ValueError:
            detail = {'detail': 'Please provide a valid index.'}
            detail['status'] = STATUS_CODE['errparam']
            logger.error(detail)
            response.data = detail
            return response

        file_name = image.file_name
        file_path = os.path.join(MEDIA_ROOT, file_name)

        logger.info(file_path)

        try:
            wrapper = FileWrapper(open(file_path, 'rb'))
        except (FileNotFoundError, IsADirectoryError) as e:
            detail = {'detail': 'No such file or directory: %s, ex: %s' % (file_name, ex)}
            detail['status'] = STATUS_CODE['non_file_exists']
            logger.error(detail)
            response.data = detail                       
            return response

        content_type = mimetypes.guess_type(file_path)[0]
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(file_path)
        logger.info(os.path.getsize(file_path))
        response['Content-Disposition'] = "attachment; filename=%s" %file_name
        return response

@api_view(['GET'])
def cover_page_api(request):
    """
    app api
    """
    response = Response()

    if request.method == 'GET':
        index = request.GET.get('index')

        try:
            image = CoverPages.objects.get('cover_page')
        except CoverPages.DoesNotExist:            
            detail = {'detail': 'No cover image.'}
            detail['status'] = STATUS_CODE['non_cover_image']
            logger.error(detail)
            response.data = detail
            return response
        except ValueError:
            detail = {'detail': 'Please provide a valid index.'}
            detail['status'] = STATUS_CODE['errparam']
            logger.error(detail)
            response.data = detail
            return response

        file_name = image.file_name
        file_path = os.path.join(MEDIA_ROOT, file_name)

        logger.info(file_path)

        try:
            wrapper = FileWrapper(open(file_path, 'rb'))
        except (FileNotFoundError, IsADirectoryError) as e:
            detail = {'detail': 'No such file or directory: %s, ex: %s' % (file_name, ex)}
            detail['status'] = STATUS_CODE['non_file_exists']
            logger.error(detail)
            response.data = detail                       
            return response

        content_type = mimetypes.guess_type(file_path)[0]
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(file_path)
        logger.info(os.path.getsize(file_path))
        response['Content-Disposition'] = "attachment; filename=%s" %file_name
        return response