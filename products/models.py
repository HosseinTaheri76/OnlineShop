from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, gettext

from colorfield.fields import ColorField


class ActiveCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class ActiveProductManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(category__is_active=True, is_active=True)


class ActiveProductVariantManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(product__category__is_active=True, product__is_active=True, is_active=True)



class ProductCategory(models.Model):
    """Category for products"""
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, unique=True, verbose_name=_('Slug'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    parent = models.ForeignKey(
        to='self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sub_categories',
        verbose_name=_('Parent category')
    )

    objects = models.Manager()
    active_manager = ActiveCategoryManager()

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Brand for products"""
    name = models.CharField(max_length=128, unique=True, verbose_name=_('Name'))

    def __str__(self):
        return self.name


class Color(models.Model):
    """table for storing colors"""
    name = models.CharField(max_length=64, unique=True, verbose_name=_('Name'))
    color = ColorField(format='hexa', unique=True, verbose_name=_('Color'))

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    """Store attributes for products like: ram size, screen resolution ..."""
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    description = models.TextField(max_length=500, blank=True, verbose_name=_('Short description'))

    def __str__(self):
        return self.name


class ProductType(models.Model):
    """Type for products like: Gpu, t-shirt ..."""
    name = models.CharField(max_length=128, unique=True, verbose_name=_('Product type'))

    attributes = models.ManyToManyField(
        ProductAttribute,
        through='ProductTypeAttribute',
        related_name='product_types',
        verbose_name=_('Attributes')
    )

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """Pair of attribute and its value foe example: core clock: 2500 Mhz"""
    product_attribute = models.ForeignKey(
        ProductAttribute,
        related_name='values',
        on_delete=models.PROTECT,
        verbose_name=_('Attribute')
    )
    attribute_value = models.CharField(max_length=255, verbose_name=_('Attribute value'))

    def __str__(self):
        return f'{self.product_attribute.name}: {self.attribute_value}'


class Product(models.Model):
    """Base Product model"""
    name = models.CharField(max_length=256, verbose_name=_('Name'))
    slug = models.SlugField(max_length=256, verbose_name=_('Slug'))  # unique or not
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    description = models.TextField(verbose_name=_('Description'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('Datetime modified'))
    score = models.PositiveSmallIntegerField(default=0, verbose_name=_('Score'), editable=False)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Category')
    )

    objects = models.Manager()
    active_manager = ActiveProductManager()

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    """Store info about each product variant for example red xl variant for t-shirt"""
    sku = models.CharField(max_length=32, unique=True, verbose_name=_('SKU'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    is_default = models.BooleanField(default=False, verbose_name=_('Is default'))
    retail_price_toman = models.PositiveIntegerField(verbose_name=_('Retail price toman'))
    retail_price_dollar = models.DecimalField(max_digits=7, decimal_places=2, verbose_name=_('Retail price dollar'))
    store_price_toman = models.PositiveIntegerField(verbose_name=_('Store price toman'))
    store_price_dollar = models.DecimalField(max_digits=7, decimal_places=2, verbose_name=_('Store price dollar'))
    is_digital = models.BooleanField(default=False, verbose_name=_('Is digital'), help_text=_('Software and ..'))
    weight = models.FloatField(verbose_name=_('Weight'), help_text=_('Enter in Kilos'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('Datetime modified'))
    attribute_values = models.ManyToManyField(
        ProductAttributeValue,
        related_name='product_variants',
        through='ProductAttributeValues',
        verbose_name=_('Specifications')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='variants',
        verbose_name=_('Product')
    )
    product_type = models.ForeignKey(
        ProductType,
        related_name='products',
        on_delete=models.PROTECT,
        verbose_name=_('Product type')
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Brand')
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Color')
    )

    objects = models.Manager()
    active_manager = ActiveProductVariantManager()

    def __str__(self):
        return f'{self.product.name}-{self.sku}'

    def get_absolute_url(self):
        return reverse('products:product-variant-detail', args=(self.sku, self.product.slug,))


class ProductImage(models.Model):
    """Images of product"""
    product_variant = models.ForeignKey(
        ProductVariant,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name=_('Product variant')
    )
    image = models.ImageField(upload_to='products/', verbose_name=_('Image'))
    is_default = models.BooleanField(default=False, verbose_name=_('Is default image'))
    alt_text = models.CharField(max_length=128, verbose_name=_('alt text'))  # auto generate

    def __str__(self):
        return self.alt_text


class ProductAttributeValues(models.Model):
    """Store related attribute-values for each product variant"""
    attribute_value = models.ForeignKey(
        ProductAttributeValue,
        on_delete=models.PROTECT,
        related_name='product_attr_values',
        verbose_name=_('Attribute Value')
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='product_attr_values',
        verbose_name=_('Product variant')
    )
    is_feature = models.BooleanField(default=False, verbose_name=_('Is feature'))

    class Meta:
        unique_together = (('attribute_value', 'product_variant'),)

    def __str__(self):
        return str(self.attribute_value)


class ProductTypeAttribute(models.Model):
    """Store attributes for each product type vise versa"""
    product_attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.PROTECT,
        related_name='type_attributes',
        verbose_name=_('Attribute')
    )

    product_type = models.ForeignKey(
        ProductType,
        related_name='type_attributes',
        on_delete=models.PROTECT,
        verbose_name=_('Type')
    )

    class Meta:
        unique_together = (('product_attribute', 'product_type'),)

    def __str__(self):
        return str(self.product_attribute)


class Stock(models.Model):
    product_variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.PROTECT,
        verbose_name=_('Product variant')
    )
    units = models.PositiveIntegerField(default=0, verbose_name=_('Remaining units'))
    units_sold = models.PositiveIntegerField(default=0, verbose_name=_('Units Sold'))
    datetime_checked = models.DateTimeField(null=True, blank=True, verbose_name=_('Datetime checked'))

    def __str__(self):
        return gettext('%(units)s remaining - %(sku)s') % {'units': self.units, 'sku': self.product_variant.sku}
