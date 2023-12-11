from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from . import models


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(TranslationAdmin):
    pass


@admin.register(models.Product)
class ProductAdmin(TranslationAdmin):
    pass
