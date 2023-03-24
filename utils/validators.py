import re


def validate_jalali_date_format(date):
    pattern = r'^\d{4}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])$'
    regex = re.compile(pattern)
    if regex.match(date):
        return True
