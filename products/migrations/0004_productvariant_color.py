# Generated by Django 4.2.7 on 2023-12-16 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_color_name_en_color_name_fa'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='color',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='products.color', verbose_name='Color'),
            preserve_default=False,
        ),
    ]
