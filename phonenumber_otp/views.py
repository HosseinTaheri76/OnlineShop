from django.http import HttpResponseNotFound
from django.shortcuts import redirect, resolve_url
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import RedirectURLMixin
from django.views.generic import FormView

# Create your views here.
from .forms import OtpRequestForm, OtpConfirmForm
from .utils import generate_otp_code


# refactored classed based view

class LoginRequestView(FormView):
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
        otp_request = form.get_object()
        otp_request.code = generate_otp_code()
        otp_request.save()
        self.request.session['otp_id'] = otp_request.id
        self.request.session['phone_number'] = form.cleaned_data['phone_number'].as_e164  # to be Json serializable
        return redirect(self.get_success_url())

    def get_success_url(self):
        success_url = super().get_success_url()
        next_page = self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
        )
        if next_page:
            return success_url + f'?{self.redirect_field_name}={next_page}'
        return success_url


class LoginConfirmView(RedirectURLMixin, FormView):
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
