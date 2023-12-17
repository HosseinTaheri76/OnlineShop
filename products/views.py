from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, F
from django.views.generic import TemplateView

from .models import (
    Product,
    ProductVariant,
    ProductAttributeValue,
    )


class ProductDetailView(TemplateView):
    template_name = 'products/product-detail.html'

    @staticmethod
    def get_product_queryset():
        return Product.active_manager.select_related('category').prefetch_related(
            Prefetch(
                lookup='variants',
                queryset=(
                    ProductVariant.objects.filter(is_active=True).
                    select_related('color').prefetch_related('images')
                ),
                to_attr='product_variants'
            ))

    @staticmethod
    def get_variant_queryset(product_id):
        return ProductVariant.objects.filter(product_id=product_id, is_active=True).prefetch_related(
            Prefetch(
                lookup='attribute_values',
                queryset=ProductAttributeValue.objects.select_related('product_attribute').annotate(
                    is_feature=F('product_attr_values__is_feature')
                ),
                to_attr='attributes'
            ))

    def get_product_variant(self, queryset):
        lookup = {}
        if sku := self.kwargs.get('variant_sku'):
            lookup['sku'] = sku
        return get_object_or_404(queryset, **lookup)

    def get_product(self, queryset):
        product_id, product_slug = self.kwargs.get('product_id'), self.kwargs.get('product_slug')
        return get_object_or_404(queryset, id=product_id, slug=product_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_queryset = self.get_product_queryset()
        product = self.get_product(product_queryset)
        context.update({
            'product': product,
            'default_variant': self.get_product_variant(self.get_variant_queryset(product.id))
        })
        return context
