from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

from .models import OneTimePasswordRequest, OneTimePasswordSetting


class PhoneNumberOtpBackend:

    def authenticate(self, request, otp_code=None, otp_id=None, otp_uuid=None, **kwargs):

        if not any([otp_id, otp_uuid]) or all([otp_id, otp_uuid]):
            return
        if not otp_code:
            return
        try:
            if otp_id:  # session auth
                otp_request = OneTimePasswordRequest.objects.get(id=otp_id)
            elif otp_uuid:  # drf
                otp_request = OneTimePasswordRequest.objects.get(uuid=otp_uuid)
        except OneTimePasswordRequest.DoesNotExist:
            return

        if self.is_valid(otp_request, otp_code):
            user = self.get_or_create_user(otp_request)
            otp_request.used = True
            otp_request.save()
            return user

    @staticmethod
    def is_valid(otp_request, otp_code):
        # maybe move logic somewhere else
        code_validity, case_sensitive = OneTimePasswordSetting.objects.get_settings('code_validity', 'case_sensitive')
        datetime_code_expires = otp_request.datetime_sent + timedelta(seconds=code_validity)
        if case_sensitive:
            code_is_correct = (otp_request.code == otp_code)
        else:
            code_is_correct = (otp_request.code.lower() == otp_code.lower())
        code_has_time = (timezone.now() <= datetime_code_expires)
        code_not_used = (otp_request.used is False)
        return all([code_is_correct, code_has_time, code_not_used])

    @staticmethod
    def get_or_create_user(otp_request):
        User = get_user_model()
        kwargs = {settings.PHONE_NUMBER_FIELD_NAME: otp_request.phone_number}
        try:
            user = User.objects.get(**kwargs)
        except User.DoesNotExist:
            user = User(**kwargs)
            if settings.FILL_USERNAME_WITH_PHONENUMBER:
                setattr(user, User.USERNAME_FIELD, otp_request.phone_number)
            user.save()
        return user
