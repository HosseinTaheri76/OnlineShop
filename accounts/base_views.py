from django.http import HttpResponseNotFound
from django.shortcuts import redirect, resolve_url
from django.conf import settings
from django.contrib.auth.views import RedirectURLMixin
from django.views.generic import FormView
from django.contrib.auth import login


class BaseLoginRequestView(FormView):
    redirect_field_name = 'next'
    redirect_authenticated = False

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated and request.user.is_authenticated:
            return redirect(resolve_url(settings.LOGIN_REDIRECT_URL))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        success_url = super().get_success_url()
        next_page = self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
        )
        if next_page:
            return success_url + f'?{self.redirect_field_name}={next_page}'
        return success_url


class BaseLoginConfirmView(RedirectURLMixin, FormView):
    redirect_authenticated = True

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated and request.user.is_authenticated:
            return redirect(self.get_success_url())
        if not self.has_permission():
            return HttpResponseNotFound()
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

    def has_permission(self):
        raise NotImplementedError

    def form_valid(self, form):
        login(self.request, form.user)
        return super().form_valid(form)
