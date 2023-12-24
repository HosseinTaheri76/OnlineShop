from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, F, Value, Case, When, fields, Count
from django.views.generic import DetailView


from .models import ProductVariant, ProductAttributeValue
from comments.views import ProductCommentPartial


class ProductVariantDetailView(DetailView):
    template_name = 'products/product-detail.html'
    context_object_name = 'product_variant'

    def get_queryset(self):
        prefetches = [
            Prefetch('product__variants', ProductVariant.objects.select_related('color').filter(is_active=True)),
            Prefetch('attribute_values', ProductAttributeValue.objects.select_related('product_attribute')
                     .annotate(is_feature=F('product_attr_values__is_feature'))),

        ]
        return (
            ProductVariant.active_manager.select_related('product', 'product__category', 'stock', 'color')
            .prefetch_related(*prefetches).annotate(
                in_stock=Case(
                    When(stock__units__gt=0, then=Value(True)),
                    default=Value(False),
                    output_field=fields.BooleanField()
                ),
                product_comments_count=Count('product__comments')
            ))

    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), sku=self.kwargs.get('sku'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_partial = ProductCommentPartial.as_view(product_id=self.object.product_id)(self.request).render()
        context['comments_partial'] = comments_partial
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
