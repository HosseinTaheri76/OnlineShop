from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from phonenumber_field.modelfields import PhoneNumberField


class OtpSettingManager(models.Manager):

    def get_settings(self, *fields):
        """ general method for retrieving settings object
        or collecting some special fields from it """

        queryset = self.get_queryset()
        if fields:
            return queryset.values_list(*fields, flat=(len(fields) == 1)).first()
        return queryset.first()


class OneTimePasswordRequest(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid4)  # for drf authentication
    phone_number = PhoneNumberField()
    code = models.CharField(max_length=16)
    used = models.BooleanField(default=False)
    datetime_sent = models.DateTimeField(auto_now_add=True)


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
        default=CODE_TYPE_NUMERICAL
    )

    code_length = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(4, 'Code length cannot be less than 4 characters.'),
            MaxValueValidator(8, 'Code length cannot be greater than 8 characters')
        ]
        , default=5
    )

    code_validity = models.PositiveSmallIntegerField(default=180)  # use same amount for code validity
    case_sensitive = models.BooleanField(default=False)
    # and resend cooldown or make separate settings ?

    objects = OtpSettingManager()

    def __str__(self):
        return 'settings'
