# Generated by Django 4.2.7 on 2023-12-11 20:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('short_description', models.CharField(max_length=1000, verbose_name='Short description')),
                ('full_description', models.TextField(verbose_name='Persian full description')),
                ('price_toman', models.PositiveIntegerField(verbose_name='Price-Toman')),
                ('price_dollar', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Price-Dollar')),
                ('thumbnail', models.ImageField(upload_to='products/', verbose_name='Main image')),
                ('score', models.PositiveSmallIntegerField(default=0, verbose_name='Score')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttributeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
            ],
        ),
        migrations.CreateModel(
            name='ProductColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_toman', models.PositiveIntegerField(verbose_name='Price')),
                ('price_dollar', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Price-Dollar')),
                ('sku', models.CharField(max_length=10, unique=True, verbose_name='SKU')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.productcolor', verbose_name='Color')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='variants', to='products.product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/', verbose_name='Image')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sub_categories', to='products.productcategory', verbose_name='Parent category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=256, verbose_name='Value')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productattribute', verbose_name='Attribute')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attrs_values', to='products.product', verbose_name='Product')),
            ],
        ),
        migrations.AddField(
            model_name='productattribute',
            name='attribute_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attributes', to='products.productattributecategory', verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='productattribute',
            name='product_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_attributes', to='products.productcategory', verbose_name='Product Category'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='products.productcategory', verbose_name='Category'),
        ),
    ]