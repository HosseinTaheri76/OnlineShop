from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from products.models import Product


class ActiveCommentManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_verified=True)


class AbstractComment(models.Model):

    COMMENT_SCORE_VERY_BAD = 1
    COMMENT_SCORE_BAD = 2
    COMMENT_SCORE_NORMAL = 3
    COMMENT_SCORE_GOOD = 4
    COMMENT_SCORE_EXCELLENT = 5

    COMMENT_SCORE_CHOICES = [
        (COMMENT_SCORE_VERY_BAD, _('Very bad')),
        (COMMENT_SCORE_BAD, _('Bad')),
        (COMMENT_SCORE_NORMAL, _('Normal')),
        (COMMENT_SCORE_GOOD, _('Good')),
        (COMMENT_SCORE_EXCELLENT, _('Excellent'))
    ]
    parent = models.ForeignKey(
        to='self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('Parent Comment')
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name='product_comments',
        null=True, blank=True,
        verbose_name=_('User')
    )
    score = models.PositiveSmallIntegerField(
        choices=COMMENT_SCORE_CHOICES,
        verbose_name=_('Score'),
        null=True,
        blank=True,
    )
    fullname = models.CharField(max_length=128, verbose_name=_('Full name'))
    email = models.EmailField(max_length=128, verbose_name=_('Email'))
    body = models.TextField(verbose_name=_('Text'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Datetime created'))

    is_verified = models.BooleanField(default=False, verbose_name=_('Is verified'))
    is_admin = models.BooleanField(default=False, verbose_name=_('Is admin'))

    objects = models.Manager()
    active_manager = ActiveCommentManager()

    class Meta:
        abstract = True


class ProductComment(AbstractComment):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.PROTECT,
        related_name='comments',
        verbose_name=_('Product')
    )
    pros = models.CharField(max_length=128, verbose_name=_('Pros'), blank=True)
    cons = models.CharField(max_length=128, verbose_name=_('Cons'), blank=True)

    # todo: add a field to store user bought product or not
    def get_pros(self):
        return self.pros.split(',')

    def get_cons(self):
        return self.cons.split(',')
