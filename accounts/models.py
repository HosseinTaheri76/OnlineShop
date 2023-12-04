from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):

    phone_number = PhoneNumberField(
        null=True, blank=True,
        db_index=True, unique=True,
        verbose_name=_('phone number'),
    )
