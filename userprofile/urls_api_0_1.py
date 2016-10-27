from django.conf.urls import url

from userprofile import views
from userprofile import records

urlpatterns = [
    #url(r'^pic/', views.FileUploadView.as_view()),
    url(r'^avatar/upload/$', views.FileUploadView.as_view()),
    url(r'^avatar/$', views.file_download_api, name='file_download_api'),
    url(r'^plate_number/$', views.plate_number_api, name='plate_number_api'),
    url(r'^vehicle_in/$', views.vehicle_in_api, name='vehicle_in_api'),
    url(r'^vehicle_out/$', views.vehicle_out_api, name='vehicle_out_api'),
    url(r'^pay_offline/$', views.pay_offline_api, name='pay_offline_api'),
    url(r'^comment/$', views.comment_api, name='comment_api'),
    url(r'^bills/$', records.bills_api, name='bills_api'),
    url(r'^prepayments/$', records.prepayments_api, name='prepayments_api'),
    url(r'^$', views.userprofile_api, name='userprofile_api'),
]

