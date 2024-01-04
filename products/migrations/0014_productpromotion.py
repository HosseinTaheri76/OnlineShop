# Generated by Django 4.2.7 on 2023-12-30 16:02

import django.core.validators
from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_alter_productvariant_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductPromotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_percent', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Discount percent')),
                ('datetime_start', models.DateTimeField(verbose_name='Start at')),
                ('datetime_end', models.DateTimeField(verbose_name='End at')),
                ('product_variants', models.ManyToManyField(related_name='promotions', to='products.productvariant')),
            ],
            managers=[
                ('active_manager', django.db.models.manager.Manager()),
            ],
        ),
    ]