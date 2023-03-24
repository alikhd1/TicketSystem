import jdatetime


def last_day_of_jalali_month(year, month):
    if month <= 6:
        return 31
    elif month <= 11:
        return 30
    elif month == 12 and (year % 4 == 3 or year % 4 == 0):
        return 30
    else:
        return 29


def get_this_month_first_and_last_day(gregorian=False):
    jalali_first_day = jdatetime.date.today()
    jalali_first_day = jdatetime.date(jalali_first_day.year, jalali_first_day.month, 1, locale='fa_IR')

    last_day = last_day_of_jalali_month(jalali_first_day.year, jalali_first_day.month)
    jalali_last_day = jdatetime.date(jalali_first_day.year, jalali_first_day.month, last_day, locale='fa_IR')

    if gregorian:
        return jalali_first_day.togregorian(), jalali_last_day.togregorian()

    return jalali_first_day, jalali_last_day


def date2jalali(g_date):
    return jdatetime.date.fromgregorian(date=g_date, locale='fa_IR') if g_date else None


def datetime2jalali(g_date):
    if g_date is None:
        return None

    return jdatetime.datetime.fromgregorian(datetime=g_date)
