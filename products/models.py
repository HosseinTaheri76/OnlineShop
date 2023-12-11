from django.db import models
from django.utils.translation import gettext_lazy as _


class ProductCategory(models.Model):
    parent = models.ForeignKey(
        to='self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sub_categories',
        verbose_name=_('Parent category')
    )
    title = models.CharField(max_length=256, verbose_name=_('Title'))


class ProductAttributeCategory(models.Model):
    title = models.CharField(max_length=256, verbose_name=_('Title'))


class ProductColor(models.Model):
    title = models.CharField(max_length=128, verbose_name=_('Title'))


class ProductAttribute(models.Model):
    title = models.CharField(max_length=128, verbose_name=_('Title'))
    product_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name='product_attributes',
        verbose_name=_('Product Category')
    )
    attribute_category = models.ForeignKey(
        ProductAttributeCategory,
        on_delete=models.PROTECT,
        related_name='attributes',
        verbose_name=_('Category')
    )


class Product(models.Model):
    title = models.CharField(max_length=256, verbose_name=_('Title'))
    short_description = models.CharField(max_length=1000, verbose_name=_('Short description'))
    full_description = models.TextField(verbose_name=_('Persian full description'))
    # price
    price_toman = models.PositiveIntegerField(verbose_name=_('Price-Toman'))
    price_dollar = models.DecimalField(default=0, max_digits=7, decimal_places=2, verbose_name=_('Price-Dollar'))

    thumbnail = models.ImageField(upload_to='products/', verbose_name=_('Main image'))
    score = models.PositiveSmallIntegerField(default=0, verbose_name=_('Score'))
    category = models.ForeignKey(
        to=ProductCategory,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Category')
    )


class ProductImage(models.Model):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Product')
    )
    image = models.ImageField(upload_to='products/', verbose_name=_('Image'))


class ProductAttributeValue(models.Model):
    value = models.CharField(max_length=256, verbose_name=_('Value'))

    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='attrs_values',
        verbose_name=_('Product')
    )
    attribute = models.ForeignKey(
        to=ProductAttribute,
        on_delete=models.CASCADE,
        verbose_name=_('Attribute')
    )


class ProductVariant(models.Model):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.PROTECT,
        related_name='variants',
        verbose_name=_('Product')
    )
    color = models.ForeignKey(
        to=ProductColor,
        on_delete=models.PROTECT,
        verbose_name=_('Color')
    )
    price_toman = models.PositiveIntegerField(verbose_name=_('Price'))
    price_dollar = models.DecimalField(default=0, max_digits=7, decimal_places=2, verbose_name=_('Price-Dollar'))
    sku = models.CharField(max_length=10, unique=True, verbose_name=_('SKU'))
