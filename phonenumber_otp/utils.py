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
    otp_setting = OneTimePasswordSetting.objects.only('code_type', 'code_length').first()
    char_domain = list(char_map[otp_setting.code_type])
    shuffle(char_domain)
    return ''.join(choices(char_domain, k=otp_setting.code_length))
