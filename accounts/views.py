from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404

from .forms import LoginRequestForm, EmailLoginConfirmForm, OtpLoginConfirmForm
from .models import OneTimePasswordRequest, OneTimePasswordSetting
from . import base_views


class LoginRequestView(base_views.BaseLoginRequestView):
    # known security issue, user can come back to this page after sending otp request,
    # filling polluting database and bombarding sms service.
    template_name = 'accounts/login-request.html'
    form_class = LoginRequestForm
    success_url = reverse_lazy('accounts:login-confirm-otp')
    redirect_authenticated = False

    def form_valid(self, form):
        session = self.request.session
        value = form.get_valid_email_or_otp_request()
        if isinstance(value, OneTimePasswordRequest):
            session['otp_id'] = value.id
            session['phone_number'] = value.phone_number.as_e164
            if 'email' in session:
                del session['email']
        elif isinstance(value, str):
            session['email'] = value
            if 'phone_number' in session:
                del session['phone_number']
        return super().form_valid(form)

    def get_success_url(self):
        if 'email' in self.request.session:
            self.success_url = reverse('accounts:login-confirm-email')
        return super().get_success_url()


class OtpLoginConfirmView(base_views.BaseLoginConfirmView):
    template_name = 'accounts/login-confirm-otp.html'
    form_class = OtpLoginConfirmForm

    def has_permission(self):
        session = self.request.session
        return 'phone_number' in session and 'email' not in session

    def form_valid(self, form):
        del self.request.session['phone_number']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        otp_id = self.request.session.get('otp_id')
        otp_settings = OneTimePasswordSetting.objects.only('code_length', 'code_type').first()
        context['remaining_cooldown'] = get_object_or_404(OneTimePasswordRequest, pk=otp_id).get_remaining_seconds()
        context.update({'code_type': otp_settings.code_type, 'code_length': range(otp_settings.code_length)})
        return context


class EmailLoginConfirmView(base_views.BaseLoginConfirmView):
    template_name = 'accounts/login-confirm-email.html'
    form_class = EmailLoginConfirmForm

    def has_permission(self):
        session = self.request.session
        return 'email' in session and 'phone_number' not in session

    def form_valid(self, form):
        del self.request.session['email']
        return super().form_valid(form)
