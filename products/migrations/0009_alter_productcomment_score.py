# Generated by Django 4.2.7 on 2023-12-21 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_productcomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcomment',
            name='score',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Very bad'), (2, 'Bad'), (3, 'Normal'), (4, 'Good'), (5, 'Excellent')], null=True, verbose_name='Score'),
        ),
    ]
