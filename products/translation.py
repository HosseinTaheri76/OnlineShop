from modeltranslation.translator import translator, TranslationOptions

from . import models


class ProductCategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


class ProductAttributeCategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


class ProductColorTranslationOptions(TranslationOptions):
    fields = ('title',)


class ProductAttributeTranslationOptions(TranslationOptions):
    fields = ('title',)


class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'full_description',)


class ProductAttributeValueTranslationOptions(TranslationOptions):
    fields = ('value',)


translator.register(models.ProductCategory, ProductCategoryTranslationOptions)
translator.register(models.ProductAttributeCategory, ProductAttributeCategoryTranslationOptions)
translator.register(models.ProductColor, ProductColorTranslationOptions)
translator.register(models.ProductAttribute, ProductAttributeTranslationOptions)
translator.register(models.Product, ProductTranslationOptions)
translator.register(models.ProductAttributeValue, ProductAttributeValueTranslationOptions)
