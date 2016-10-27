from django.conf.urls import url

from parking import views, roadside

urlpatterns = [
    #url(r'^$', views.parkinglot, name='parkinglot'),
    # TODO  define regular expression
    #url(r'^(?P<parking_lot_id>[0-9]*)/$', views.parkingspace, name='parkingspace'),
    url(r'^in/$', views.vehicle_in_api, name='vehicle_in_api'),
    url(r'^out/$', views.vehicle_out_api, name='vehicle_out_api'),
    url(r'^parking/$', views.parking_api, name='parking_api'),
    url(r'^parking_lots/$', views.parkinglot_api, name='parkinglot_api'),
    url(r'^parking_lots/image/$', views.parking_lot_image_api, name='parking_lot_image_api'),
    url(r'^get_private_key/$', views.get_private_key_api, name='get_private_key_api'),
    url(r'^get_public_key/$', views.get_public_key_api, name='get_public_key_api'),
    url(r'^roadside/register/$', roadside.roadside_register_api, name='roadside_register_api'),
    url(r'^$', views.parkinglot_api, name='parkinglot_api'),
]

