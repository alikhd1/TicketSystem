import datetime

import jdatetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create a new coupon and save it to the database
from models import Coupon, UsedCoupon, Base
from utils.date import last_day_of_jalali_month, get_this_month_first_and_last_day

engine = create_engine('sqlite:///data.db')
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

date = datetime.datetime(2023, 4, 1)
fa_date = jdatetime.date(1402, 2, 1, locale='fa_IR')

first_day = jdatetime.date.today()
first_day = jdatetime.date(first_day.year, first_day.month, 1, locale='fa_IR')
print(first_day.togregorian())

last_day = last_day_of_jalali_month(first_day.year, first_day.month)
jalali_last_day = jdatetime.date(first_day.year, first_day.month, last_day, locale='fa_IR')
print(jalali_last_day.togregorian())

print(first_day)
print(jalali_last_day)


coupon = Coupon(expired_time=date)
coupon2 = Coupon(expired_time=date)

session.add(coupon)
session.add(coupon2)
# session.commit()

coupons = session.query(Coupon).all()
f_coupons = session.query(Coupon).filter(Coupon.code == '3RX87RXYI0').first()
d_from, d_to = get_this_month_first_and_last_day(gregorian=True)
this_month_use = session.query(UsedCoupon).filter(
    Coupon.code == '3RX87RXYI0', UsedCoupon.use_time.between(d_from, d_to))

print(len(list(this_month_use)))
# print(len(f_coupons))
# print(f_coupons.used_coupons)
us = UsedCoupon(coupon=f_coupons)
session.add(us)
session.commit()

print(f_coupons)


# coupon = Coupon(datetime.datetime(2023, 4, 1))
# coupon.save()
# coupon = Coupon.get_by_code(code='V9ZJ9U3RCM')

# Mark the coupon as used and save the used coupon to the database
# used_coupon = UsedCoupon(coupon, datetime.now())
# used_coupon.save()
