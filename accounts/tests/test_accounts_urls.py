from django.urls import resolve, reverse
from django.test import SimpleTestCase

from ..views import LoginRequestView, OtpLoginConfirmView, EmailLoginConfirmView


class TestAccountsUrls(SimpleTestCase):

    def test_login_request_url(self):
        resolved_url = resolve(reverse('accounts:login-request'))
        self.assertEqual(resolved_url.func.view_class, LoginRequestView)

    def test_otp_login_confirm_url(self):
        resolved_url = resolve(reverse('accounts:login-confirm-otp'))
        self.assertEqual(resolved_url.func.view_class, OtpLoginConfirmView)

    def test_email_login_confirm_url(self):
        resolved_url = resolve(reverse('accounts:login-confirm-email'))
        self.assertEqual(resolved_url.func.view_class, EmailLoginConfirmView)
