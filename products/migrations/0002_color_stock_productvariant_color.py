# Generated by Django 4.2.7 on 2023-12-15 14:22

import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Name')),
                ('color', colorfield.fields.ColorField(default='#FFFFFFFF', image_field=None, max_length=25, samples=None, unique=True, verbose_name='Color')),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('units', models.PositiveIntegerField(default=0, verbose_name='Remaining units')),
                ('units_sold', models.PositiveIntegerField(default=0, verbose_name='Units Sold')),
                ('datetime_checked', models.DateTimeField(blank=True, null=True, verbose_name='Datetime checked')),
                ('product_variant', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='products.productvariant', verbose_name='Product variant')),
            ],
        ),
    ]
