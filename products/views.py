from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import DetailView

from comments.views import ProductCommentPartial
from .queries import product_detail_info
from .models import ProductPromotion


class ProductVariantDetailView(DetailView):
    template_name = 'products/product-detail.html'
    context_object_name = 'product_variant'

    def get_queryset(self):
        return product_detail_info()

    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), sku=self.kwargs.get('sku'))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        comments_partial_response = ProductCommentPartial.as_view(product_variant=self.object)(request)
        if isinstance(comments_partial_response, HttpResponseRedirect):
            return comments_partial_response
        return self.render_to_response(
            self.get_context_data(
                object=self.object,
                comments_partial=comments_partial_response.rendered_content,
                active_tab=self.get_active_tab(comments_partial_response)
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['promotions_available'] = ProductPromotion.active_manager.exists()
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_active_tab(self, comments_partial):
        """get which tab should be active when template renders"""
        if 'page' in self.request.GET or comments_partial.context_data['form'].errors:
            return 'comments'
        return 'review'
