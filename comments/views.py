from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import BaseFormView
from django.utils.translation import gettext_lazy as _

from .forms import ProductCommentForm


class ProductCommentPartial(ListView, BaseFormView):
    template_name = 'comments/comments.html'
    form_class = ProductCommentForm
    paginate_by = 3
    product_variant = None
    context_object_name = 'comments'
    success_message = _('Your comment submitted successfully, it will be shown when it become verified.')

    def get_queryset(self):
        return self.product_variant.product.comments.all()

    def form_valid(self, form):
        commenter_user = self.request.user if self.request.user.is_authenticated else None
        comment = form.save(commit=False)
        comment.user = commenter_user
        comment.parent = form.parent_comment
        comment.product_id = self.product_variant.product_id
        if commenter_user and commenter_user.is_staff:
            comment.is_verified = True
            comment.is_admin = True
        else:
            messages.success(self.request, self.success_message)
        comment.save()
        self.save_info(form)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.product_variant.get_absolute_url() + f'?page={self.request.GET.get("page", 1)}'

    def save_info(self, form):
        """save user fullname and email for next comment"""
        save_info = form.cleaned_data.get('save_info')
        self.request.session['comment_name'] = form.cleaned_data['fullname'] if save_info else ''
        self.request.session['comment_email'] = form.cleaned_data['email'] if save_info else ''

    def get_initial(self):
        initial = super().get_initial()
        initial['fullname'] = self.request.session.get('comment_name', '')
        initial['email'] = self.request.session.get('comment_email', '')
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['comments_list'] = self.object_list
        return kwargs

    def form_invalid(self, form):
        """Message non_field errors"""
        if '__all__' in form.errors:
            messages.error(self.request, form.errors['__all__'])
        return super().form_invalid(form)
