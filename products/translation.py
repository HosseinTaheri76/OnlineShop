from modeltranslation.translator import translator, TranslationOptions

from . import models


class ProductImageTranslationOptions(TranslationOptions):
    fields = ('alt_text',)


class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description')


class ProductTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


class ProductAttributeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class ProductAttributeValueTranslationOptions(TranslationOptions):
    fields = ('attribute_value',)


class ProductCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug',)


class BrandTranslationOptions(TranslationOptions):
    fields = ('name',)


class ColorTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(models.ProductImage, ProductImageTranslationOptions)
translator.register(models.Product, ProductTranslationOptions)
translator.register(models.ProductType, ProductTypeTranslationOptions)
translator.register(models.ProductAttribute, ProductAttributeTranslationOptions)
translator.register(models.ProductAttributeValue, ProductAttributeValueTranslationOptions)
translator.register(models.ProductCategory, ProductCategoryTranslationOptions)
translator.register(models.Brand, BrandTranslationOptions)
translator.register(models.Color, ColorTranslationOptions)
