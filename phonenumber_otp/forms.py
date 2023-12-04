from datetime import timedelta

from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone

from phonenumber_field.formfields import PhoneNumberField

from .models import OneTimePasswordRequest, OneTimePasswordSetting


class OtpRequestForm(forms.Form):
    phone_number = PhoneNumberField()

    def clean(self):
        cd = self.cleaned_data
        phone_number = cd.get('phone_number')
        code_validity = OneTimePasswordSetting.objects.get_settings('code_validity')
        active_request = OneTimePasswordRequest.objects.filter(
            datetime_sent__lt=timezone.now() + timedelta(seconds=code_validity),
            phone_number=phone_number,
            used=False
        ).first()
        if active_request:
            cooldown_remaining = active_request.datetime_sent + timedelta(seconds=code_validity) - timezone.now()
            raise forms.ValidationError(f'you must wait for more {cooldown_remaining} seconds', 'cooldown')
        return cd

    def get_object(self) -> OneTimePasswordRequest:
        assert len(self.errors) == 0, 'Must be called only when form is valid'
        return OneTimePasswordRequest(**self.cleaned_data)


class OtpConfirmForm(forms.Form):
    code = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def get_user(self):
        otp_id = self.request.session.get('otp_id')
        otp_code = self.cleaned_data.get('code')
        return authenticate(self.request, otp_id=otp_id, otp_code=otp_code)
