from uuid import uuid4
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _, gettext
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class UsableOtpRequestManager(models.Manager):

    def get_queryset(self):
        code_validity = OneTimePasswordSetting.objects.get_settings('code_validity')
        return super().get_queryset().filter(
            datetime_sent__gte=timezone.now() - timedelta(seconds=code_validity),
            used=False
        )


class OtpSettingManager(models.Manager):

    def get_settings(self, *fields):
        """ general method for retrieving settings object
        or collecting some special fields from it """
        queryset = self.get_queryset()
        if fields:
            return queryset.values_list(*fields, flat=(len(fields) == 1)).first()
        return queryset.first()


class CustomUser(AbstractUser):
    phone_number = PhoneNumberField(
        null=True, blank=True,
        db_index=True, unique=True,
        verbose_name=_('phone number'),
    )
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)


class OneTimePasswordRequest(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid4, verbose_name=_('UUID'))  # for drf authentication
    phone_number = PhoneNumberField(verbose_name=_('Phone number'))
    code = models.CharField(max_length=16, verbose_name=_('One time password'))
    used = models.BooleanField(default=False, verbose_name=_('Is code used'))
    datetime_sent = models.DateTimeField(auto_now_add=True, verbose_name=_('Datetime sms sent'))

    objects = models.Manager()
    usable_requests = UsableOtpRequestManager()

    def __str__(self):
        return gettext('Otp with uuid=%(uuid)s') % {'uuid': self.uuid}

    def get_remaining_seconds(self):
        code_validity = OneTimePasswordSetting.objects.get_settings('code_validity')
        remaining = (self.datetime_sent + timedelta(seconds=code_validity) - timezone.now()).seconds
        return remaining if 0 <= remaining <= code_validity else 0

    class Meta:
        verbose_name = _('One time password request')
        verbose_name_plural = _('One time password requests')


class OneTimePasswordSetting(models.Model):
    CODE_TYPE_NUMERICAL = 'num'
    CODE_TYPE_ALPHANUMERIC = 'aln'
    CODE_TYPE_ALPHABETIC = 'alp'

    CODE_TYPE_CHOICES = [
        (CODE_TYPE_NUMERICAL, 'Numeric'),
        (CODE_TYPE_ALPHANUMERIC, 'Alphanumeric'),
        (CODE_TYPE_ALPHABETIC, 'Alphabetic'),
    ]

    code_type = models.CharField(
        max_length=3,
        choices=CODE_TYPE_CHOICES,
        default=CODE_TYPE_NUMERICAL,
        verbose_name=_('Password type')
    )

    code_length = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(4, 'Code length cannot be less than 4 characters.'),
            MaxValueValidator(8, 'Code length cannot be greater than 8 characters')
        ]
        , default=5, verbose_name=_('Password length')
    )

    code_validity = models.PositiveSmallIntegerField(default=180, verbose_name=_('Password validity duration'))
    case_sensitive = models.BooleanField(default=False, verbose_name=_('Password case-sensitive'))
    # and resend cooldown or make separate settings ?

    objects = OtpSettingManager()

    def __str__(self):
        return gettext('One time password settings')

    class Meta:
        verbose_name = _('Settings')
        verbose_name_plural = _('One time password setting')
