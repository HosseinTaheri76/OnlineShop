from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login-request/', views.LoginRequestView.as_view(), name='login-request'),
    path('login-confirm-otp/', views.OtpLoginConfirmView.as_view(), name='login-confirm-otp'),
    path('login-confirm-email/', views.EmailLoginConfirmView.as_view(), name='login-confirm-email'),
]
