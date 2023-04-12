import datetime

import secrets
import string

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from utils.barcode import generate_checksum

Base = declarative_base()


class Coupon(Base):
    __tablename__ = 'coupon'

    id = Column(Integer, primary_key=True, autoincrement=True)
    expired_time = Column(Date)
    code = Column(String, unique=True)
    use_limit = Column(Integer, default=1)
    full_name = Column(String)
    national_code = Column(String)
    personnel_code = Column(String)
    used_coupons = relationship("UsedCoupon", back_populates="coupon")

    def __init__(self, expired_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expired_time = expired_time
        self.generate_code()

    def generate_code(self):
        code = ''.join(secrets.choice(string.digits) for _ in range(12))
        while code[0] == '0':
            #  because of ups prefix barcodes with 0, barcode should not be started with 0
            code = ''.join(secrets.choice(string.digits) for _ in range(12))
        self.code = generate_checksum(code)

    def __len__(self):
        return len(self.used_coupons)

    def __repr__(self):
        return f'{self.id}: {self.code}'


class UsedCoupon(Base):
    __tablename__ = 'used_coupon'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey('coupon.id'))
    use_time = Column(DateTime)

    coupon = relationship("Coupon", back_populates="used_coupons")

    def __init__(self, coupon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coupon = coupon
        self.use_time = datetime.datetime.now()

    def __repr__(self):
        return f'{self.id}: {self.use_time}'
