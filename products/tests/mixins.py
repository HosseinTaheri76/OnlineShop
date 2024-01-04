from django.test import TestCase

from .. import models


class ProductTestMixin(TestCase):

    def setUp(self):
        self.category_graphic_cards = models.ProductCategory.objects.create(name='graphic cards', slug='graphic-cards')
        self.category_laptops = models.ProductCategory.objects.create(name='laptops', slug='laptops')

        self.brand_asus = models.Brand(name='asus')
        self.brand_msi = models.Brand(name='msi')

        self.product_type_gpu = models.ProductType.objects.create(name='gpu')
        self.product_type_laptop = models.ProductType.objects.create(name='laptop')

        self.color_red = models.Color(name='red', color='#ff0000')
        self.color_green = models.Color(name='green', color='#00ff00')
        self.color_blue = models.Color(name='blue', color='#0000ff')

    def create_attributes(self):
        pass