from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException
from django.contrib.auth import get_user_model, authenticate

from config.utils.forms.bootstrap import BootstrapFormMixin
from .models import OneTimePasswordRequest, OneTimePasswordSetting


class OtpRequestForm(BootstrapFormMixin, forms.Form):
    phone_or_email = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': _('Enter your Email or Phone number'), 'autofocus': True}),
        label=_('Phonenumber or Email')
    )

    @staticmethod
    def is_phone_number_or_email(value):
        """
        check value is an email, phone number or none of them.
        """
        is_email, is_phone_number = False, False
        try:
            validate_email(value)
            is_email = True
        except ValidationError:
            try:
                number = PhoneNumber.from_string(value)
                is_phone_number = number.is_valid()
            except NumberParseException:
                pass
        return 'email' if is_email else 'phone_number' if is_phone_number else None

    @staticmethod
    def can_request_otp(phone_number):
        """
        Validate form to find out user can request otp or must wait for cooldown.
        """
        code_validity = OneTimePasswordSetting.objects.get_settings('code_validity')
        active_request = OneTimePasswordRequest.objects.filter(
            datetime_sent__lt=timezone.now() + timedelta(seconds=code_validity),
            phone_number=phone_number,
            used=False
        ).first()
        cooldown_remaining = 0
        if active_request:
            cooldown_remaining = (
                    active_request.datetime_sent + timedelta(seconds=code_validity) - timezone.now()
            ).seconds
        return active_request is None, cooldown_remaining

    @staticmethod
    def can_authenticate_with_email(email):
        User = get_user_model()
        try:
            User.objects.get(email=email)
            return True
        except User.DoesNotExists:
            return False

    def clean_phone_or_email(self):
        phone_or_email = self.cleaned_data.get('phone_or_email')  # field value
        is_phone_or_email = self.is_phone_number_or_email(phone_or_email)  # is a valid email or phone or none

        if not is_phone_or_email:  # user entered invalid value
            raise forms.ValidationError(_('Please Enter a valid phone number or email address.'))
        if is_phone_or_email == 'phone_number':  # user entered phone number
            can_request_otp, cooldown = self.can_request_otp(phone_or_email)  # can request otp ?
            if not can_request_otp:
                raise forms.ValidationError(_('You have to wait %(cooldown)s seconds before you can request again.') % {
                    'cooldown': cooldown
                })
        if is_phone_or_email == 'email' and not self.can_authenticate_with_email(phone_or_email):  # user entered email
            raise forms.ValidationError(  # can auth with email
                _('User with this email address not found please try logging in with phone number.')
            )
        return phone_or_email


class OtpConfirmForm(forms.Form):
    code = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def get_user(self):
        otp_id = self.request.session.get('otp_id')
        otp_code = self.cleaned_data.get('code')
        return authenticate(self.request, otp_id=otp_id, otp_code=otp_code)
