from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import BaseFormView
from django.utils.translation import gettext_lazy as _

from .models import ProductComment
from .forms import ProductCommentForm


class ProductCommentPartial(ListView, BaseFormView):
    template_name = 'comments/comments.html'
    form_class = ProductCommentForm
    paginate_by = 10
    product_id = None
    context_object_name = 'comments'
    success_message = _('Your comment submitted successfully, it will be shown when it become verified.')

    def get_queryset(self):
        return ProductComment.active_manager.filter(product_id=self.product_id)

    def form_valid(self, form):
        parent_id = self.request.POST.get('parent_id')
        parent_comment = (
            get_object_or_404(ProductComment.active_manager.filter(product_id=self.product_id), pk=parent_id)
            if parent_id else None
        )
        commenter_user = self.request.user if self.request.user.is_authenticated else None
        comment = form.save(commit=False)
        comment.user = commenter_user
        comment.parent = parent_comment
        comment.product_id = self.product_id
        comment.save()
        messages.success(self.request, self.success_message)
        return super().form_invalid(self.form_class())

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().post(request, *args, **kwargs)
