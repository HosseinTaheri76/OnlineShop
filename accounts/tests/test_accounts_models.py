from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from phonenumber_field.phonenumber import PhoneNumber

from ..models import OneTimePasswordRequest, OneTimePasswordSetting
from ..utils import generate_otp_code


class TestOTPRequestModel(TestCase):
    """
        Testing OneTimePasswordRequest model, all requests has 180 seconds time validity.
    """
    def setUp(self):
        self.otp_settings = OneTimePasswordSetting.objects.create(
            code_validity=180,
        )

    @staticmethod
    def get_otp_request():
        return OneTimePasswordRequest.objects.create(
            phone_number=PhoneNumber.from_string('09123380189'),
            code=generate_otp_code()
        )

    def test_get_remaining_seconds_works_correctly(self):
        initial_datetime = timezone.now()
        target_datetime_1 = initial_datetime + timedelta(seconds=21)
        target_datetime_2 = initial_datetime + timedelta(seconds=195)
        target_datetime_3 = initial_datetime + timedelta(seconds=85)

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()
            frozen_datetime.move_to(target_datetime_1)
            self.assertEqual(self.otp_settings.code_validity - 21, otp_request.get_remaining_seconds())

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()
            frozen_datetime.move_to(target_datetime_2)
            self.assertEqual(0, otp_request.get_remaining_seconds())

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()
            frozen_datetime.move_to(target_datetime_3)
            self.assertEqual(self.otp_settings.code_validity - 85, otp_request.get_remaining_seconds())

    def test_get_remaining_seconds_wont_return_negative_value(self):
        initial_datetime = timezone.now()
        target_datetime_1 = initial_datetime + timedelta(seconds=self.otp_settings.code_validity)
        target_datetime_2 = initial_datetime + timedelta(seconds=self.otp_settings.code_validity + 50)

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()
            frozen_datetime.move_to(target_datetime_1)
            self.assertEqual(0, otp_request.get_remaining_seconds())

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()
            frozen_datetime.move_to(target_datetime_2)
            self.assertEqual(0, otp_request.get_remaining_seconds())

    def test_usable_manager_if_otp_request_expires(self):
        initial_datetime = timezone.now()
        target_datetime_1 = initial_datetime + timedelta(seconds=70)
        target_datetime_2 = initial_datetime + timedelta(seconds=self.otp_settings.code_validity)
        target_datetime_3 = initial_datetime + timedelta(seconds=self.otp_settings.code_validity + 1)

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()
            frozen_datetime.move_to(target_datetime_1)
            self.assertEqual(1, OneTimePasswordRequest.usable_requests.count())
            otp_request.delete()

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()
            frozen_datetime.move_to(target_datetime_2)
            self.assertEqual(1, OneTimePasswordRequest.usable_requests.count())
            otp_request.delete()

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()
            frozen_datetime.move_to(target_datetime_3)
            self.assertEqual(0, OneTimePasswordRequest.usable_requests.count())
            otp_request.delete()

    def test_usable_manager_if_otp_request_used(self):
        otp_request_1 = self.get_otp_request()
        self.get_otp_request()
        self.get_otp_request()
        otp_request_1.used = True
        otp_request_1.save()
        self.assertEqual(OneTimePasswordRequest.usable_requests.count(), 2)

    def test_usable_manager_used_and_expired(self):
        initial_datetime = timezone.now()
        target_datetime_1 = initial_datetime + timedelta(seconds=90)
        target_datetime_2 = initial_datetime + timedelta(seconds=self.otp_settings.code_validity - 2)
        target_datetime_3 = initial_datetime + timedelta(seconds=self.otp_settings.code_validity + 3)

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()  # not used and not expired
            frozen_datetime.move_to(target_datetime_1)
            self.assertEqual(1, OneTimePasswordRequest.usable_requests.count())
            otp_request.delete()

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()  # not expired but used
            otp_request.used = True
            otp_request.save()
            frozen_datetime.move_to(target_datetime_2)
            self.assertEqual(0, OneTimePasswordRequest.usable_requests.count())
            otp_request.delete()

        with freeze_time(initial_datetime) as frozen_datetime:
            otp_request = self.get_otp_request()  # expired and used
            otp_request.used = True
            otp_request.save()
            frozen_datetime.move_to(target_datetime_3)
            self.assertEqual(0, OneTimePasswordRequest.usable_requests.count())
            otp_request.delete()


class TestOTPSettingsModel(TestCase):
    def setUp(self):
        self.otp_settings = OneTimePasswordSetting.objects.create()

    def test_code_generator_function_code_length(self):
        code = generate_otp_code()
        self.assertEqual(len(code), self.otp_settings.code_length)
        self.otp_settings.code_length = 6
        self.otp_settings.save()
        code = generate_otp_code()
        self.assertEqual(len(code), self.otp_settings.code_length)

    def test_code_generator_function_code_type(self):
        code = generate_otp_code()
        self.assertTrue(code.isdigit())
        # change settings to alphabetic
        self.otp_settings.code_type = self.otp_settings.CODE_TYPE_ALPHABETIC
        self.otp_settings.save()
        code = generate_otp_code()
        self.assertTrue(code.isalpha())
        # change to alphanumeric
        self.otp_settings.code_type = self.otp_settings.CODE_TYPE_ALPHANUMERIC
        self.otp_settings.save()
        code = generate_otp_code()
        self.assertTrue(code.isalnum())
