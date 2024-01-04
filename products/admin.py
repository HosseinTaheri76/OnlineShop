from django.contrib import admin
from django.db.models import Count, Prefetch
from django.utils.translation import gettext_lazy as _

from modeltranslation import admin as trans_admin

from . import models
from .forms import ProductAdminForm, ProductPromotionAdminForm, ProductVariantAdminForm


class ActivePromotionFilter(admin.SimpleListFilter):
    title = _('Is active')
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return [
            ('true', 'Yes'),
            ('false', 'No')
        ]

    def queryset(self, request, queryset):
        active_promotions = models.ProductPromotion.active_manager.values_list('id', flat=True)
        if self.value() == 'true':
            return queryset.filter(id__in=active_promotions)
        elif self.value() == 'false':
            return queryset.exclude(id__in=active_promotions)


class ProductImageInline(trans_admin.TranslationTabularInline):
    model = models.ProductImage
    extra = 0
    min_num = 1


class ProductAttributeValuesInline(admin.TabularInline):
    model = models.ProductAttributeValues
    extra = 0
    min_num = 1
    autocomplete_fields = ['attribute_value', ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attribute_value__product_attribute')


class ProductTypeAttributeInline(admin.TabularInline):
    model = models.ProductTypeAttribute
    extra = 0
    min_num = 1


class StockInline(admin.TabularInline):
    model = models.Stock
    min_num = 1
    max_num = 1


@admin.register(models.ProductType)
class ProductTypeAdmin(trans_admin.TranslationAdmin):
    inlines = [ProductTypeAttributeInline, ]


@admin.register(models.ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [StockInline, ProductImageInline, ProductAttributeValuesInline]
    autocomplete_fields = ['product', ]
    list_select_related = ['product', 'brand', 'product_type', 'color', 'stock']
    form = ProductVariantAdminForm
    search_fields = [
        'sku', 'product__name_fa__contains', 'product__name_en__icontains', 'brand__name_fa', 'brand__name_en',
        'color__name_fa', 'color__name_en', 'product__category__name_fa', 'product__category__name_en',
        'product_type__name_fa', 'product_type__name_en'
    ]
    fieldsets = (
        (
            _('General info'),
            {"fields": ("product", "sku", "product_type", "brand", "color", "weight", "thumbnail_image")}),
        (
            _("Price info"),
            {"fields": ("retail_price_toman", "store_price_toman", "retail_price_dollar", "store_price_dollar")}
        ),
        (
            _('Status'),
            {"fields": ("is_digital", "is_active", "is_default")}
        ),
    )
 

@admin.register(models.Product)
class ProductAdmin(trans_admin.TranslationAdmin):
    form = ProductAdminForm
    fieldsets = (
        (_('General info'), {"fields": ("name_fa", "name_en", "slug_fa", "slug_en", "category")}),
        (_('Status'), {"fields": ("is_active",)}),
        (_("Description"), {"fields": ("description_fa", "description_en")})
    )
    search_fields = [
        "name_fa__contains", "name_en__icontains", "category__name_fa__contains", "category__name_en__icontains"
    ]


@admin.register(models.ProductAttribute)
class ProductAttributeAdmin(trans_admin.TranslationAdmin):
    search_fields = ['name_fa__contains', 'name_en__icontains']


@admin.register(models.ProductAttributeValue)
class ProductAttributeValueAdmin(trans_admin.TranslationAdmin):
    search_fields = ['product_attribute__name_fa__contains', 'product_attribute__name_en__icontains']
    autocomplete_fields = ['product_attribute', ]
    list_select_related = ['product_attribute', ]


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(trans_admin.TranslationAdmin):
    pass  # todo: add mptt later on


@admin.register(models.Brand)
class BrandAdmin(trans_admin.TranslationAdmin):
    list_display = ['__str__', 'product_variants_count']
    search_fields = ['name_fa__contains', 'name_en__icontains']

    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related('products')
            .annotate(product_variants_count=Count('products'))
        )

    @admin.display(description=_('Number of product variants'), ordering='product_variants_count')
    def product_variants_count(self, brand):
        return brand.product_variants_count


@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'color', 'product_variants_count']
    list_editable = ['color']
    search_fields = ['name_fa__contains', 'name_en__icontains']

    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related('products')
            .annotate(product_variants_count=Count('products'))
        )

    @admin.display(description=_('Number of product variants'), ordering='product_variants_count')
    def product_variants_count(self, color):
        return color.product_variants_count


@admin.register(models.ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    form = ProductPromotionAdminForm

    list_display = ['__str__', 'is_active', 'remaining_time', 'active', 'variants_count']
    list_editable = ['active', ]
    list_filter = [ActivePromotionFilter, ]
    autocomplete_fields = ['product_variants', ]

    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related('product_variants')
            .annotate(product_variants_count=Count('product_variants'))
        )

    @admin.display(boolean=True, description=_('Is active'))
    def is_active(self, promotion):
        return promotion.is_active()

    @admin.display(description=_('Remaining time'))
    def remaining_time(self, promotion):
        return promotion.remaining_time()

    @admin.display(ordering='product_variants_count', description=_('Affected product variants count'))
    def variants_count(self, promotion):
        return promotion.product_variants_count
