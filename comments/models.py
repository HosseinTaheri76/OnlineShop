from django.db import models
from django.db.models import Sum, Count, Value
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.functions import Coalesce

from jalali_date import datetime2jalali, date2jalali

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
    # field that stores comment score already applied to related object or not
    score_applied = models.BooleanField(default=False, editable=False)
    fullname = models.CharField(max_length=128, verbose_name=_('Full name'))
    email = models.EmailField(max_length=128, verbose_name=_('Email'))
    body = models.TextField(verbose_name=_('Text'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Datetime created'))

    is_verified = models.BooleanField(default=False, verbose_name=_('Is verified'))
    is_admin = models.BooleanField(default=False, verbose_name=_('Is admin'))

    objects = models.Manager()
    active_manager = ActiveCommentManager()

    def _get_verification_status(self):
        db_value = self.__class__.objects.only('is_verified').get(pk=self.id).is_verified
        if (not db_value) and self.is_verified:
            return 'verified'
        if db_value and (not self.is_verified):
            return 'unverified'

    def date_created_jalali(self):
        return date2jalali(self.datetime_created.date()).strftime('%Y/%-m/%-d')

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

    def _update_product_score(self):
        """Update related product if needed"""
        if self.pk and self.score and (verification_status := self._get_verification_status()):
            rated_comments = self.product.comments(manager='active_manager').filter(score_applied=True).aggregate(
                score_sum=Coalesce(Sum('score'), Value(0)), comments_count=Coalesce(Count('id'), Value(0))
            )
            if verification_status == 'verified' and not self.score_applied:
                self.product.score = round(
                    (rated_comments['score_sum'] + self.score) / (rated_comments['comments_count'] + 1), 1
                )
                self.product.save()
                self.score_applied = True
            elif verification_status == 'unverified' and self.score_applied:
                self.product.score = round(
                    (rated_comments['score_sum'] - self.score) / (rated_comments['comments_count'] - 1), 1
                )
                self.product.save()
                self.score_applied = False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self._update_product_score()
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
