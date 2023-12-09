from .models import CustomUser
from django.conf import settings

from .models import OneTimePasswordRequest, OneTimePasswordSetting


class _BaseBackend:
    def get_user(self, user_id):
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
        return user if user.is_active else None


class PhoneNumberOtpBackend(_BaseBackend):

    def authenticate(self, request, otp_code=None, otp_id=None, otp_uuid=None, **kwargs):
        """
        Get or create a user based on id or uuid of an otp_request if, credentials are valid.
        """
        if not any([otp_id, otp_uuid]) or all([otp_id, otp_uuid]):
            return
        if not otp_code:
            return
        try:
            if otp_id:  # session auth
                otp_request = OneTimePasswordRequest.usable_requests.get(id=otp_id)
            elif otp_uuid:  # drf
                otp_request = OneTimePasswordRequest.usable_requests.get(uuid=otp_uuid)
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
        case_sensitive = OneTimePasswordSetting.objects.get_settings('case_sensitive')
        if case_sensitive:
            code_is_correct = (otp_request.code == otp_code)
        else:
            code_is_correct = (otp_request.code.lower() == otp_code.lower())
        code_not_used = (otp_request.used is False)
        return code_is_correct and code_not_used

    @staticmethod
    def get_or_create_user(otp_request):
        kwargs = {settings.PHONE_NUMBER_FIELD_NAME: otp_request.phone_number}
        try:
            user = CustomUser.objects.get(**kwargs)
        except CustomUser.DoesNotExist:
            user = CustomUser(**kwargs)
            if settings.FILL_USERNAME_WITH_PHONENUMBER:
                setattr(user, CustomUser.USERNAME_FIELD, otp_request.phone_number)
            user.save()
        return user


class EmailPasswordBackend(_BaseBackend):

    def authenticate(self, request, email=None, password=None, **kwargs):
        if not all([email, password]):
            return
        try:
            user = CustomUser.objects.get(email__iexact=email)
            return user if user.check_password(password) else None
        except CustomUser.DoesNotExist:
            return
