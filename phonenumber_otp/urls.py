from django.urls import path

from . import views

app_name = 'phonenumber_otp'

urlpatterns = [
    path('login-request/', views.LoginRequestView.as_view(), name='login-request'),
    path('login-confirm/', views.LoginConfirmView.as_view(), name='login-confirm'),
]
