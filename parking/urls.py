from django.conf.urls import url

from parking import views

urlpatterns = [
    url(r'^$', views.parkinglot, name='parkinglot'),
    # TODO  define regular expression
    url(r'^(?P<parking_lot_id>[0-9]*)/$', views.parkingspace, name='parkingspace'),
    url(r'^v0.1/parking/$', views.parkinglot_api, name='parkinglot_api'),
]

