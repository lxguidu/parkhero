"""parkhero URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^parkhero/admin/', include(admin.site.urls)),
    url(r'^parkhero/parking/', include('parking.urls')),
    url(r'^parkhero/v0.1/parking/', include('parking.urls_api_0_1')),
    url(r'^parkhero/v0.1/user/', include('userprofile.urls_api_0_1')),
    url(r'^parkhero/v0.1/account/', include('account.urls_api_0_1')),
    url(r'^parkhero/v0.1/billing/', include('billing.urls_api_0_1')),
    url(r'^parkhero/v0.1/operation/', include('operation.urls_api_0_1')),
    url(r'^parkhero/v0.1/version/', include('version.urls_api_0_1')),
    url(r'^parkhero/api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]

