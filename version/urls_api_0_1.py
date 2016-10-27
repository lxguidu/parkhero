from django.conf.urls import url

from version import views

urlpatterns = [
    url(r'^$', views.version_info_api, name='version_info_api'),
    url(r'^download/$', views.download_api, name='download_api'),
    url(r'^slide_show/$', views.slide_show_api, name='slide_show_api'),
    url(r'^startup_page/$', views.startup_page_api, name='startup_page_api'),
    url(r'^index_page/$', views.index_page_api, name='index_page_api'),
    url(r'^cover_page/$', views.cover_page_api, name='cover_page_api'),
]

