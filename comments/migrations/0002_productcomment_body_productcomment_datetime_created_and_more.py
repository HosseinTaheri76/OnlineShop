# Generated by Django 4.2.7 on 2023-12-24 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcomment',
            name='body',
            field=models.TextField(default='asdsd', verbose_name='Text'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productcomment',
            name='datetime_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Datetime created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productcomment',
            name='email',
            field=models.EmailField(default='a@a.com', max_length=128, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productcomment',
            name='fullname',
            field=models.CharField(default='asdsd', max_length=128, verbose_name='Full name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productcomment',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Is admin'),
        ),
        migrations.AddField(
            model_name='productcomment',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='Is verified'),
        ),
        migrations.AddField(
            model_name='productcomment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='replies', to='comments.productcomment', verbose_name='Parent Comment'),
        ),
        migrations.AddField(
            model_name='productcomment',
            name='score',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Very bad'), (2, 'Bad'), (3, 'Normal'), (4, 'Good'), (5, 'Excellent')], null=True, verbose_name='Score'),
        ),
        migrations.AddField(
            model_name='productcomment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_comments', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
