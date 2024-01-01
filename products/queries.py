from django.db.models import Prefetch, F, Count, Q


from comments.models import ProductComment
from products.models import ProductVariant, ProductAttributeValue


def product_detail_info():
    product__variants = Prefetch(
        'product__variants', ProductVariant.objects.select_related('color').filter(is_active=True)
    )
    attribute_values = Prefetch(
        'attribute_values',
        ProductAttributeValue.objects.select_related('product_attribute')
        .annotate(is_feature=F('product_attr_values__is_feature'))
    )
    product__comments = Prefetch(
        'product__comments',
        ProductComment.active_manager.select_related('user').filter(parent__isnull=True)
        .prefetch_related(Prefetch('replies', ProductComment.active_manager.filter(parent__isnull=False)))
    )

    return (
        ProductVariant.active_manager.get_variants_list().select_related('color')
        .prefetch_related('images', product__variants, attribute_values, product__comments).annotate(
            product__comments_count=Count(
                'product__comments',
                filter=Q(product__comments__is_verified=True, product__comments__parent__isnull=True)
            ),
        )
    )
