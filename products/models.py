import random
from decimal import Decimal

from django.db import models
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value, OuterRef, Subquery
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, gettext
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db import transaction

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

    def get_variants_list(self):
        """Return a query set of product variants with product title and price info annotated."""
        discount_percent_subquery = (
            ProductPromotion.active_manager.filter(product_variants__id=OuterRef('id'))
            .values_list('discount_percent', flat=True)[:1]
        )

        return (
            self.select_related('product', 'product__category', 'stock')
            .annotate(
                in_stock=Case(
                    When(stock__units__gt=0, then=Value(True)),
                    default=Value(False),
                    output_field=models.BooleanField()
                ),
                discount_percent=Coalesce(Subquery(discount_percent_subquery), Value(0))
            )
        )


class ActiveProductPromotionManager(models.Manager):

    def get_queryset(self):
        now = timezone.now()
        return super().get_queryset().filter(datetime_start__lt=now, datetime_end__gt=now)


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
    score = models.FloatField(verbose_name=_('Score'), editable=False, default=0)
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
    thumbnail_image = models.ImageField(upload_to='products/', verbose_name=_('Thumbnail image'))
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

    class Meta:
        unique_together = (('product', 'color'),)

    def __str__(self):
        return f'{self.product.name}-{self.sku}'

    def get_absolute_url(self):
        return reverse('products:product-variant-detail', args=(self.sku, self.product.slug,))

    def get_random_related_variants(self):
        """Method for displaying related products (their default variant) in product detail page"""
        related_product__product_variants_ids = (
            ProductVariant.active_manager.filter(product__category_id=self.product.category_id, is_default=True)
            .exclude(product_id=self.product_id)
        )
        try:
            chosen_ids = random.sample(list(related_product__product_variants_ids), 8)
        except ValueError:
            chosen_ids = related_product__product_variants_ids

        return ProductVariant.active_manager.get_variants_list().filter(id__in=chosen_ids)

    def get_price_toman(self):
        """This method is intended to be called on objects of a queryset with annotated discount_percent"""
        return int(self.store_price_toman * (1 - self.discount_percent / 100))

    def get_price_dollar(self):
        """This method is intended to be called on objects of a queryset with annotated discount_percent"""
        return round(self.store_price_dollar * Decimal(1 - self.discount_percent / 100), 2)

    def replace_default_variant(self):
        """When setting is_default to True checks if there is already default variant for that product, if was it will
           replace it.
        """
        db_value = self.__class__.objects.only('is_default').get(pk=self.pk).is_default
        memory_value = self.is_default
        if (db_value != memory_value) and memory_value:
            self.product.variants.exclude(pk=self.pk).filter(is_default=True).update(is_default=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.replace_default_variant()
            super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Images of product"""
    product_variant = models.ForeignKey(
        ProductVariant,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name=_('Product variant')
    )
    image = models.ImageField(upload_to='products/', verbose_name=_('Image'))
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


class ProductPromotion(models.Model):
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name=_('Discount percent')
    )
    product_variants = models.ManyToManyField(ProductVariant, related_name='promotions')
    datetime_start = models.DateTimeField(verbose_name=_('Start at'))
    datetime_end = models.DateTimeField(verbose_name=_('End at'))

    active_manager = ActiveProductPromotionManager()
    objects = models.Manager()
