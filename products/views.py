from random import sample

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Prefetch, F, Value, Case, When, fields, Count, Q
from django.views.generic import DetailView

from .models import ProductVariant, ProductAttributeValue, Product
from comments.views import ProductCommentPartial
from comments.models import ProductComment


class ProductVariantDetailView(DetailView):
    template_name = 'products/product-detail.html'
    context_object_name = 'product_variant'

    def get_queryset(self):
        prefetches = [
            Prefetch('product__variants', ProductVariant.objects.select_related('color').filter(is_active=True)),
            Prefetch('attribute_values', ProductAttributeValue.objects.select_related('product_attribute')
                     .annotate(is_feature=F('product_attr_values__is_feature'))),
            Prefetch('product__comments', ProductComment.active_manager.select_related('user')
                     .filter(parent__isnull=True)
                     .prefetch_related(Prefetch('replies', ProductComment.active_manager.all())))
        ]
        return (
            ProductVariant.active_manager.select_related('product', 'product__category', 'stock', 'color')
            .prefetch_related(*prefetches).annotate(
                in_stock=Case(
                    When(stock__units__gt=0, then=Value(True)),
                    default=Value(False),
                    output_field=fields.BooleanField()
                ),
                product_comments_count=Count(
                    'product__comments',
                    filter=Q(product__comments__is_verified=True, product__comments__parent__isnull=True)
                )
            ))

    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), sku=self.kwargs.get('sku'))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        comments_partial = ProductCommentPartial.as_view(product_variant=self.object)(self.request)
        if isinstance(comments_partial, HttpResponseRedirect):
            return comments_partial
        comments_partial = comments_partial.render()
        context = self.get_context_data(
            object=self.object,
            comments_partial=comments_partial,
            active_tab=self.get_active_tab(comments_partial)
        )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_active_tab(self, comments_partial):
        """get which tab should be active when template renders"""
        if 'page' in self.request.GET or comments_partial.context_data['form'].errors:
            return 'comments'
        return 'review'


class RefinedProductVariantDetailView(DetailView):

    def get_queryset(self):
        product = get_object_or_404(
            Product.active_manager.prefetch_related('variants'),
            slug=self.kwargs['product_slug']
        )
        product__variants = product.variants(manager='active_manager').select_related('color')

        product_variant = (
            product.variants(manager='active_manager').select_related('product__category', 'stock')
            .prefetch_related(
                'images',
                Prefetch(
                    'attribute_values',
                    (
                        ProductAttributeValue.objects.select_related('product_attribute')
                        .annotate(is_feature=F('product_attr_values__is_feature'))
                    )
                )
            )
        )
        product__comments = (
            product.comments(manager='active_manager').select_related('user').filter(parent__isnull=True)
            .prefetch_related(Prefetch('replies', ProductComment.active_manager.filter(parent__isnull=False)))
        )
        related_product__variants_ids = (
            ProductVariant.active_manager.exclude(product_id=product.id)
            .filter(product__category_id=product.category_id, is_default=True)
            .values_list('id', flat=True)
        )
        try:
            chosen_ids = sample(list(related_product__variants_ids), 8)
        except ValueError:
            chosen_ids = related_product__variants_ids

        related_product__variants = ProductVariant.objects.select_related('product').filter(id__in=chosen_ids)
