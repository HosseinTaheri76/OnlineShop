from django.test import TestCase
from django.urls import reverse

from ..models import (
    ProductCategory,
    Brand,
    Color,
    ProductAttribute,
    ProductType,
    ProductAttributeValue,
    Product,
    ProductVariant,
    ProductAttributeValues
)


class TestProductDetailView(TestCase):

    @classmethod
    def setUpTestData(cls):
        ProductCategory.objects.create(name='graphic cards', slug='graphic-cards')
        Brand.objects.create(name='Asus')
        Color.objects.bulk_create([Color(name='red', color='#ff0000'), Color(name='green', color='#00ff00')])
        ProductType.objects.create(name='gpu')
        ProductAttribute.objects.bulk_create([
            ProductAttribute(name='core clock'), ProductAttribute(name='memory clock'),
            ProductAttribute(name='boost clock'), ProductAttribute(name='cuda cores'),
        ])
        ProductAttributeValue.objects.bulk_create([
            ProductAttributeValue(product_attribute_id=1, attribute_value='1960 Mhz'),  # variant 1
            ProductAttributeValue(product_attribute_id=1, attribute_value='2300 Mhz'),  # core clock # variant2
            ProductAttributeValue(product_attribute_id=2, attribute_value='12000 Mhz'),  # variant 1
            ProductAttributeValue(product_attribute_id=2, attribute_value='16000 Mhz'),  # memory clock variant2
            ProductAttributeValue(product_attribute_id=3, attribute_value='2100 Mhz'),  # variant 1
            ProductAttributeValue(product_attribute_id=3, attribute_value='2500 Mhz'),  # boost clock variant 2
            ProductAttributeValue(product_attribute_id=4, attribute_value='12650'),  # variant 1
            ProductAttributeValue(product_attribute_id=4, attribute_value='16848'),  # cuda cores variant 2
        ])
        cls.product = Product.objects.create(name='RTX 4090', slug='rtx-4090', description='lorem ...', category_id=1)
        cls.product_variant_1 = ProductVariant.objects.create(
            sku='123', is_default=True, retail_price_toman='123000', store_price_toman='125000',
            retail_price_dollar=22.5, store_price_dollar=24.00, weight=3.2, product_id=cls.product.id,
            product_type_id=1, brand_id=1, color_id=1
        )
        cls.product_variant_2 = ProductVariant.objects.create(
            sku='321', is_default=False, retail_price_toman='143000', store_price_toman='155000',
            retail_price_dollar=25, store_price_dollar=28.00, weight=3.5, product_id=cls.product.id,
            product_type_id=1, brand_id=1, color_id=2
        )
        ProductAttributeValues.objects.bulk_create([
            ProductAttributeValues(product_variant_id=cls.product_variant_1.id, attribute_value_id=1, is_feature=True),
            ProductAttributeValues(product_variant_id=cls.product_variant_2.id, attribute_value_id=2, is_feature=True),
            ProductAttributeValues(product_variant_id=cls.product_variant_1.id, attribute_value_id=3, is_feature=True),
            ProductAttributeValues(product_variant_id=cls.product_variant_2.id, attribute_value_id=4, is_feature=True),
            ProductAttributeValues(product_variant_id=cls.product_variant_1.id, attribute_value_id=5, is_feature=True),
            ProductAttributeValues(product_variant_id=cls.product_variant_2.id, attribute_value_id=6, is_feature=True),
            ProductAttributeValues(product_variant_id=cls.product_variant_1.id, attribute_value_id=7, is_feature=True),
            ProductAttributeValues(product_variant_id=cls.product_variant_2.id, attribute_value_id=8, is_feature=True)
        ])

    def test_only_shows_related_specification(self):
        response = self.client.get(reverse('products:product-detail', args=(self.product.id, self.product.slug)))
        self.assertContains(response, '1960 Mhz')
        self.assertNotContains(response, '2300 Mhz')
        self.assertContains(response, '12000 Mhz')
        self.assertNotContains(response, '16000 Mhz')
        self.assertContains(response, '2100 Mhz')
        self.assertNotContains(response, '2500 Mhz')
        self.assertContains(response, '12650')
        self.assertNotContains(response, '168484')

    def test_does_not_show_inactive_colors(self):
        response = self.client.get(reverse('products:product-detail', args=(self.product.id, self.product.slug)))
        self.assertContains(response, '#00ff00')
        self.assertContains(response, '#ff0000')
        self.product_variant_2.is_active = False
        self.product_variant_2.save()
        response = self.client.get(reverse('products:product-detail', args=(self.product.id, self.product.slug)))
        self.assertNotContains(response, '#00ff00')
        self.assertContains(response, '#ff0000')

    def test_raises_404_if_inactive(self):
        ProductVariant.objects.update(is_active=False)
        response = self.client.get(reverse('products:product-detail', args=(self.product.id, self.product.slug)))
        self.assertEqual(response.status_code, 404)
        ProductVariant.objects.update(is_active=True)

    def test_raises_404_if_product_in_active(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get(reverse('products:product-detail', args=(self.product.id, self.product.slug)))
        self.assertEqual(response.status_code, 404)


