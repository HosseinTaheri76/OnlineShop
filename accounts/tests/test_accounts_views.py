from datetime import timedelta

from django.test import TestCase, override_settings
from freezegun import freeze_time
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from phonenumber_field.phonenumber import PhoneNumber

from ..models import CustomUser, OneTimePasswordSetting, OneTimePasswordRequest


class TestLoginRequestView(TestCase):
    url = reverse_lazy('accounts:login-request')

    def setUp(self):
        self.otp_settings = OneTimePasswordSetting.objects.create()
        self.user = CustomUser.objects.create_user(
            username='Hossein',
            email='hossein76@gmail.com',
            phone_number=PhoneNumber.from_string('09302844505'),
            password='123'
        )

    def test_page_is_ok_and_right_template_used(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login-request.html')

    def test_sending_valid_email_redirects_to_email_confirm(self):
        response = self.client.post(self.url, {'phone_or_email': self.user.email})
        self.assertRedirects(response, reverse('accounts:login-confirm-email'))

    def test_sending_non_existent_email_shows_correct_error(self):
        response = self.client.post(self.url, {'phone_or_email': 'someOne@yahoo.com'})
        self.assertContains(
            response,
            _('User with this email address not found please try logging in with phone number.')
        )

    def test_sending_valid_phone_number_redirects_to_otp_confirm(self):
        response = self.client.post(self.url, {'phone_or_email': '09124470199'})
        self.assertRedirects(response, reverse('accounts:login-confirm-otp'))

    def test_sending_no_email_or_phone_shows_correct_error(self):
        response = self.client.post(self.url, {'phone_or_email': 'something'})
        self.assertContains(response, _('Please Enter a valid phone number or email address.'))

    @override_settings(LANGUAGE_CODE='en-us')
    def test_requesting_otp_before_cooldown_ends_shows_correct_error(self):
        initial_datetime = timezone.now()
        target_datetime = initial_datetime + timedelta(seconds=self.otp_settings.code_validity - 60)
        with freeze_time(initial_datetime) as frozen_datetime:
            self.client.post(self.url, {'phone_or_email': self.user.phone_number})
            frozen_datetime.move_to(target_datetime)
            response = self.client.post(self.url, {'phone_or_email': self.user.phone_number})
        self.assertContains(response, 'You have to wait 60 seconds before you can request again.')

    def test_login_request_view_redirects_authenticated_users(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_login_request_view_redirects_with_url_params(self):
        new_url = self.url + f'?next=/admin/'

        response = self.client.post(new_url, {'phone_or_email': self.user.phone_number})
        self.assertRedirects(response, reverse('accounts:login-confirm-otp') + f'?next=/admin/')

        response = self.client.post(new_url, {'phone_or_email': self.user.email})
        self.assertRedirects(response, reverse('accounts:login-confirm-email') + f'?next=/admin/')


class TestOtpLoginConfirmView(TestCase):
    url = reverse_lazy('accounts:login-confirm-otp')

    def setUp(self):
        self.otp_settings = OneTimePasswordSetting.objects.create()
        self.user = CustomUser.objects.create_user(
            username='Hossein',
            email='hossein76@gmail.com',
            phone_number=PhoneNumber.from_string('09302844505'),
            password='123'
        )

    def test_view_raises_404_if_otp_id_not_in_session(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        # test works correctly if otp_id in session
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.phone_number})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_user_is_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_user_authenticates_with_correct_otp_code(self):
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.phone_number})
        code = OneTimePasswordRequest.objects.first().code
        response = self.client.post(self.url, {'otp': code}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_user_wont_authenticate_with_expired_otp_code(self):
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.phone_number})
        code = OneTimePasswordRequest.objects.first().code
        initial_datetime = timezone.now()
        target_datetime = initial_datetime + timedelta(seconds=self.otp_settings.code_validity + 60)
        with freeze_time(initial_datetime) as frozen_datetime:
            frozen_datetime.move_to(target_datetime)
            response = self.client.post(self.url, {'otp': code})
        self.assertContains(response, _('The code is invalid or expired.'))
        self.assertFalse(response.context['user'].is_authenticated)

    def test_user_wont_authenticated_with_used_otp_code(self):
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.phone_number})
        otp_request = OneTimePasswordRequest.objects.first()
        otp_request.used = True
        otp_request.save()
        response = self.client.post(self.url, {'otp': otp_request.code})
        self.assertContains(response, _('The code is invalid or expired.'))
        self.assertFalse(response.context['user'].is_authenticated)

    def test_user_wont_authenticate_with_blank_otp_code(self):
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.phone_number})
        response = self.client.post(self.url, {'otp': ''})
        self.assertFalse(response.context['user'].is_authenticated)


class TestEmailLoginConfirmView(TestCase):
    url = reverse_lazy('accounts:login-confirm-email')

    def setUp(self):
        self.otp_settings = OneTimePasswordSetting.objects.create()
        self.user = CustomUser.objects.create_user(
            username='Hossein',
            email='hossein76@gmail.com',
            phone_number=PhoneNumber.from_string('09302844505'),
            password='123'
        )

    def test_view_raises_404_if_email_not_in_session(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        # test works correctly if email in session
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.email})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_authenticates_with_correct_password(self):
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.email})
        response = self.client.post(self.url, {'password': '123'}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_user_wont_authenticates_with_invalid_password(self):
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.email})
        response = self.client.post(self.url, {'password': '567'}, follow=True)
        self.assertContains(response, _('invalid password!'))
        self.assertFalse(response.context['user'].is_authenticated)

    def test_view_redirects_if_user_is_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_user_wont_authenticates_with_blank_password(self):
        self.client.post(reverse('accounts:login-request'), {'phone_or_email': self.user.email})
        response = self.client.post(self.url, {'password': ''}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
