#-*- coding: utf-8 -*-
from django.conf.urls import url

from operation import views

urlpatterns = [
    url(r'^vehicle_in/$', views.vehicle_in_api, name='vehicle_in_api'),
    url(r'^vehicle_out/$', views.vehicle_out_api, name='vehicle_out_api'),
    url(r'^offline_payment/$', views.offline_payment_api, name='offline_payment_api'),
    url(r'^online_payment/$', views.online_payment_api, name='online_payment_api'),
    url(r'^finance/$', views.Finance.as_view(), name='Finance'),
    url(r'^prepayment/$', views.prepayment_api, name='prepayment_api'),
    url(r'^parklots/$', views.ParkLot.as_view(), name='ParkLot'),
    #url(r'^parking_lots/$', views.parking_lots_api, name='parking_lots_api'),
    #url(r'^parking_lots/upload_tool_info/$', views.upload_tool_info_api, name='upload_tool_info_api'),
    url(r'^parking_lots/image/$', views.parking_lot_image_api, name='parking_lot_image_api'),
    url(r'^app_version/$', views.app_version_api, name='app_version_api'),
    #url(r'^app/version/upload/$', views.app_package_upload_api, name='app_package_upload_api'),
    url(r'^app_pack_upload/$', views.app_package_upload_api, name='app_package_upload_api'),
    url(r'^app_startup_page/$', views.app_startup_image_api, name='app_startup_image_api'),
    url(r'^app_index_page/$', views.app_index_image_api, name='app_index_image_api'),
    url(r'^app_cover_page/$', views.app_cover_image_api, name='app_cover_image_api'),
    url(r'^end_user/user_info/$', views.end_user_info_api, name='end_user_info_api'),
    url(r'^end_user/comments/$', views.end_user_comments_api, name='end_user_comments_api'),
    url(r'^parkinglot_online/$', views.parkinglot_online_api, name='parkinglot_online_api'),
    url(r'^parkinglot_connected/$', views.parkinglot_connected_api, name='parkinglot_connected_api'),
    url(r'^parkinglot_disconnected/$', views.parkinglot_disconnected_api, name='parkinglot_disconnected_api'),
    #url(r'^mobile_app/version/$', views.file_upload_api, name='file_upload_api'),
]

