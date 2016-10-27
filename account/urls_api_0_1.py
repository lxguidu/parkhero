from django.conf.urls import url

from account import views

#from account.paypasswd import PaymentPassword
#from account.loginpasswd import reset_password_api, update_password_api

urlpatterns = [
    url(r'^login/$', views.login_api, name='login_api'),
    #url(r'^web_login/$', views.web_login_api, name='web_login_api'),
    url(r'^logout/$', views.logout_api, name='logout_api'),
    url(r'^verify/$', views.Verify.as_view(), name='Verify'),
    url(r'^register/$', views.Register.as_view(), name='Register'),
    url(r'^loginpasswd/$', views.LoginPassword.as_view(),
                              name='LoginPassword'),    
    url(r'^payment_password/$', views.PaymentPassword.as_view(),
                              name='PaymentPassword'),
    url(r'^operator/$', views.Operator.as_view(), name='Operator'),
    url(r'^role/$', views.Role_Op.as_view(), name='Role'),
    url(r'^backperm/$', views.BackPerm.as_view(), name='BackendPerm'),
]

