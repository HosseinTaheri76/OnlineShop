from random import choices, shuffle
from string import ascii_lowercase, digits

from .models import OneTimePasswordSetting


def generate_otp_code():
    # otp setting should be a singleton model.
    char_map = {
        OneTimePasswordSetting.CODE_TYPE_NUMERICAL: digits,
        OneTimePasswordSetting.CODE_TYPE_ALPHANUMERIC: ascii_lowercase + digits,
        OneTimePasswordSetting.CODE_TYPE_ALPHABETIC: ascii_lowercase
    }
    code_type, code_length = OneTimePasswordSetting.objects.get_settings('code_type', 'code_length')
    char_domain = list(char_map[code_type])
    shuffle(char_domain)
    return ''.join(choices(char_domain, k=code_length))
