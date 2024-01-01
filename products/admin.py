from django.contrib import admin

from modeltranslation import admin as trans_admin

from . import models
from .forms import ProductAdminForm, ProductPromotionAdminForm


class ProductImageInline(trans_admin.TranslationTabularInline):
    model = models.ProductImage
    extra = 0


class ProductAttributeValuesInline(admin.TabularInline):
    model = models.ProductAttributeValues
    extra = 0


class ProductTypeAttributeInline(admin.TabularInline):
    model = models.ProductTypeAttribute
    extra = 0


class StockInline(admin.TabularInline):
    model = models.Stock


@admin.register(models.ProductType)
class ProductTypeAdmin(trans_admin.TranslationAdmin):
    inlines = [ProductTypeAttributeInline, ]


@admin.register(models.ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [StockInline, ProductImageInline, ProductAttributeValuesInline]


@admin.register(models.Product)
class ProductAdmin(trans_admin.TranslationAdmin):
    form = ProductAdminForm


@admin.register(models.ProductAttribute)
class ProductAttributeAdmin(trans_admin.TranslationAdmin):
    pass


@admin.register(models.ProductAttributeValue)
class ProductAttributeValueAdmin(trans_admin.TranslationAdmin):
    pass


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(trans_admin.TranslationAdmin):
    pass


@admin.register(models.Brand)
class BrandAdmin(trans_admin.TranslationAdmin):
    pass


@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    form = ProductPromotionAdminForm

