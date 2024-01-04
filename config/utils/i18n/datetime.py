from django.utils.translation import get_language, gettext
from django.conf import settings

from jalali_date import datetime2jalali, date2jalali


def translate_datetime(original_datetime):
    lang = get_language()
    format_str = settings.DEFAULT_DATETIME_FORMAT
    if lang == 'fa':
        return datetime2jalali(original_datetime).strftime(format_str)
    return original_datetime.strftime(format_str)


def translate_date(original_date):
    lang = get_language()
    format_str = settings.DEFAULT_DATETIME_FORMAT
    if lang == 'fa':
        return date2jalali(original_date).strftime(format_str)
    return original_date.strftime(format_str)


def format_timedelta(timedelta):
    # Calculate total seconds
    total_seconds = int(timedelta.total_seconds())

    # Calculate days, hours, minutes, and seconds
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the timedelta as a string
    formatted_timedelta = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)

    # Add days if there are any
    if days:
        formatted_timedelta = gettext('%(days)s days, %(time)s' % {'days': days, 'time': formatted_timedelta})

    return formatted_timedelta
