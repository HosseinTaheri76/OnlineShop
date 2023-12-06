from django.http import HttpResponseNotFound
from django.shortcuts import redirect, resolve_url
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import RedirectURLMixin
from django.views.generic import FormView
from phonenumber_field.phonenumber import PhoneNumber

# Create your views here.
from .forms import OtpRequestForm, OtpConfirmForm
from .utils import generate_otp_code
from .models import OneTimePasswordRequest


# refactored classed based view

class OtpRequestView(FormView):
    # known security issue, user can come back to this page after sending otp request,
    # filling polluting database and bombarding sms service.
    template_name = 'phonenumber_otp/login_request.html'
    redirect_field_name = 'next'
    form_class = OtpRequestForm
    success_url = reverse_lazy('phonenumber_otp:login-confirm')
    redirect_authenticated = False

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated and request.user.is_authenticated:
            return resolve_url(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        session = self.request.session
        phone_or_email = form.cleaned_data.get('phone_or_email')
        input_type = form.is_phone_number_or_email(phone_or_email)
        if input_type == 'phone_number':
            otp_request = OneTimePasswordRequest(phone_number=PhoneNumber.from_string(phone_or_email))
            otp_request.code = generate_otp_code()
            otp_request.save()
            if 'email' in session:
                del session['email']
            session['otp_id'] = otp_request.id
            session['phone_number'] = form.cleaned_data['phone_number'].as_e164  # to be Json serializable
        else:
            if 'phone_number' in session:
                del session['phone_number']
            session['email'] = phone_or_email
        return redirect(self.get_success_url())

    def get_success_url(self):
        if 'email' in self.request.session:
            self.success_url = reverse_lazy('pages:home')
        success_url = super().get_success_url()
        next_page = self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
        )
        if next_page:
            return success_url + f'?{self.redirect_field_name}={next_page}'
        return success_url


class OtpConfirmView(RedirectURLMixin, FormView):
    template_name = 'phonenumber_otp/login_confirm.html'
    form_class = OtpConfirmForm
    redirect_authenticated = False

    # Login_redirect_url should work , user with no active session redirect should have dynamic
    # redirect url
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated and request.user.is_authenticated:
            return redirect(self.success_url())
        if 'otp_id' not in request.session:
            return HttpResponseNotFound()  # otp_id not in session
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        form.add_error('code', 'Invalid code !')
        return super().form_invalid(form)
