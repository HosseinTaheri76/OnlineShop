from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException
from django.contrib.auth import authenticate

from config.utils.forms.bootstrap import BootstrapFormMixin
from .models import OneTimePasswordRequest, CustomUser
from .utils import generate_otp_code


class LoginRequestForm(BootstrapFormMixin, forms.Form):
    phone_or_email = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': _('Enter your Email or Phone number'), 'autofocus': True}),
        label=_('Phonenumber or Email')
    )

    def is_input_email(self):
        phone_or_email = self.cleaned_data.get('phone_or_email')
        try:
            validate_email(phone_or_email)
            return True
        except ValidationError:
            return False

    def is_input_phone_number(self):
        phone_or_email = self.cleaned_data.get('phone_or_email')
        try:
            number = PhoneNumber.from_string(phone_or_email)
            return number.is_valid()
        except NumberParseException:
            return False

    @staticmethod
    def can_request_otp(phone_number):
        """
        Validate form to find out user can request otp or must wait for cooldown.
        """
        active_request = OneTimePasswordRequest.usable_requests.filter(phone_number=phone_number).first()
        cooldown_remaining = 0
        if active_request:
            cooldown_remaining = active_request.get_remaining_seconds()
        return active_request is None, cooldown_remaining

    @staticmethod
    def can_authenticate_with_email(email):
        try:
            CustomUser.objects.get(email=email)
            return True
        except CustomUser.DoesNotExist:
            return False

    def clean_phone_or_email(self):
        phone_or_email = self.cleaned_data.get('phone_or_email')  # field value

        if self.is_input_phone_number():  # user entered phone number
            can_request_otp, cooldown = self.can_request_otp(phone_or_email)  # can request otp ?
            if not can_request_otp:
                raise forms.ValidationError(
                    _('You have to wait %(cooldown)s seconds before you can request again.') % {'cooldown': cooldown}
                    , 'cooldown-is-active'
                )
            return phone_or_email

        elif self.is_input_email():  # user entered email
            if not self.can_authenticate_with_email(phone_or_email):
                raise forms.ValidationError(  # can auth with email
                    _('User with this email address not found please try logging in with phone number.'),
                    'email-not-found'
                )
            return phone_or_email

        raise forms.ValidationError(
            _('Please Enter a valid phone number or email address.'), 'invalid-email-or-phone'
        )

    def get_valid_email_or_otp_request(self):
        """
        Create an otp_request and return it if user entered phone number and has no limits or
        returns email if email exists.
        """
        assert len(self.errors) == 0, 'Should be called only when form is valid'
        phone_or_email = self.cleaned_data['phone_or_email']
        if self.is_input_phone_number():
            phone_number = PhoneNumber.from_string(phone_or_email)
            otp_request = OneTimePasswordRequest(phone_number=phone_number)
            otp_request.code = generate_otp_code()
            otp_request.save()
            return otp_request
        elif self.is_input_email():
            return phone_or_email


class OtpLoginConfirmForm(BootstrapFormMixin, forms.Form):
    otp = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.user = None
        super().__init__(*args, **kwargs)

    def clean_otp(self):
        otp_id = self.request.session.get('otp_id')
        otp_code = self.cleaned_data.get('otp')
        self.user = authenticate(self.request, otp_id=otp_id, otp_code=otp_code)
        if not self.user:
            raise forms.ValidationError(_('The code is invalid or expired.'), 'invalid-expired')
        return otp_code


class EmailLoginConfirmForm(BootstrapFormMixin, forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Enter your password'), 'autofocus': True}),
        label=_('Password')
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.user = None
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        email = self.request.session.get('email')
        self.user = authenticate(self.request, email=email, password=password)
        if not self.user:
            raise forms.ValidationError(_('invalid password!'), 'invalid-password')
        return password
