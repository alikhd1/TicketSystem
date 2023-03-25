import jdatetime

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QTableView, QMainWindow, QGridLayout
from PyQt5.QtCore import Qt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Coupon, UsedCoupon, Base
from utils.date import get_this_month_first_and_last_day, date2jalali
from utils.excel import save_to_excel
from utils.validators import validate_jalali_date_format


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the database connection
        self.coupon = None
        engine = create_engine('sqlite:///data.db')
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

        layout = QGridLayout(self)

        self.label1 = QtWidgets.QLabel('کد')
        self.name_label = QtWidgets.QLabel('نام')
        self.national_label = QtWidgets.QLabel('کد ملی')
        self.personnel_label = QtWidgets.QLabel('شماره پرسنلی')
        self.result = QtWidgets.QLabel('')
        self.code = QtWidgets.QLineEdit()
        self.name_input = QtWidgets.QLineEdit()
        self.national_input = QtWidgets.QLineEdit()
        self.personnel_input = QtWidgets.QLineEdit()

        self.button__save = QPushButton('ذخیره', self)
        self.button__save.clicked.connect(self.save_info)
        self.button__save.setEnabled(False)

        self.label2 = QLabel(self)
        self.result_icon = QPixmap('')

        self.label2.setPixmap(self.result_icon)

        layout.addWidget(self.label1, 0, 0)
        layout.addWidget(self.code, 0, 1)

        layout.addWidget(self.result, 0, 5)
        layout.addWidget(self.label2, 0, 6)

        layout.addWidget(self.name_label, 1, 0)
        layout.addWidget(self.name_input, 1, 1)

        layout.addWidget(self.national_label, 1, 2)
        layout.addWidget(self.national_input, 1, 3)

        layout.addWidget(self.personnel_label, 1, 4)
        layout.addWidget(self.personnel_input, 1, 5)

        layout.addWidget(self.button__save, 1, 6)

        # set layout properties
        # layout.setColumnStretch(0, 0)
        # layout.setColumnStretch(1, 0)
        # layout.setColumnStretch(2, 1)
        # layout.setRowStretch(0, 5)
        # layout.setRowStretch(1, 10)

        self.code.returnPressed.connect(self.check_code)
        self.button__check = QPushButton('بررسی', self)
        self.button__check.clicked.connect(self.check_code)

        self.button__submit = QPushButton('ثبت', self)
        self.button__submit.setEnabled(False)
        self.button__submit.clicked.connect(self.submit)

        self.use_table_view = QTableView(self)

        self.use_model = QStandardItemModel(self.use_table_view)
        self.use_model.setHorizontalHeaderLabels(["ساعت", "تاریخ", "روز"])
        self.use_table_view.setModel(self.use_model)

        check_coupons_layout = QtWidgets.QFormLayout()
        # check_coupons_layout.addRow(self.label1, self.code)
        check_coupons_layout.addRow(layout)
        check_coupons_layout.addRow(self.button__check)
        check_coupons_layout.addRow(self.button__submit)
        check_coupons_layout.addRow(self.use_table_view)

        # Create the UI elements
        self.table_view = QTableView(self)

        self.model = QStandardItemModel(self.table_view)
        self.model.setHorizontalHeaderLabels(
            ["Check", "شناسه", "کد", "تاریخ اعبار", "محدودیت استفاده(ماه)", "دفعات استفاده"])
        self.table_view.setModel(self.model)
        self.table_view.setColumnWidth(0, 25)
        self.table_view.setColumnWidth(1, 50)

        self.coupon_count_input = QLineEdit()
        self.coupon_expire_input = QLineEdit()
        self.coupon_use_limit_input = QLineEdit()
        self.create_coupon_button = QPushButton('ایجاد')

        # Set up the UI layout
        coupons_layout = QVBoxLayout()
        coupons_layout.addWidget(self.table_view)
        add_coupon_layout = QHBoxLayout()
        add_coupon_layout.addWidget(QLabel('تعداد'))
        add_coupon_layout.addWidget(self.coupon_count_input)
        add_coupon_layout.addWidget(QLabel('تاریخ اعتبار'))
        add_coupon_layout.addWidget(self.coupon_expire_input)
        add_coupon_layout.addWidget(QLabel('محدودیت'))
        add_coupon_layout.addWidget(self.coupon_use_limit_input)
        add_coupon_layout.addWidget(self.create_coupon_button)
        coupons_layout.addLayout(add_coupon_layout)
        self.setLayout(coupons_layout)

        # Connect the UI signals
        self.create_coupon_button.clicked.connect(self.add_coupon)

        # Load the existing coupons from the database and display them in the UI
        self.load_coupons()

        central_widget = QtWidgets.QTabWidget()

        tab1 = QtWidgets.QWidget()
        tab1.setLayout(check_coupons_layout)
        central_widget.addTab(tab1, "بررسی کوپن")

        tab2 = QtWidgets.QWidget()
        tab2.setLayout(coupons_layout)
        central_widget.addTab(tab2, "کوپن ها")

        self.setCentralWidget(central_widget)

    def load_coupons(self):
        self.model.removeRows(0, self.model.rowCount())
        coupons = self.session.query(Coupon).all()
        for coupon in coupons:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckState(Qt.Unchecked)
            checkbox_item.setCheckable(True)

            jdate = date2jalali(coupon.expired_time)

            items = [checkbox_item, QStandardItem(str(coupon.id)), QStandardItem(coupon.code),
                     QStandardItem(jdate.strftime("%Y/%m/%d")), QStandardItem(str(coupon.use_limit)),
                     QStandardItem(str(len(coupon)))]
            self.model.appendRow(items)

    def check_code(self):
        import datetime

        code = self.code.text().upper()
        coupon = self.session.query(Coupon).filter(Coupon.code == code).first()
        today = datetime.date.today()
        used_coupons = []

        self.name_input.setText('')
        self.national_input.setText('')
        self.personnel_input.setText('')

        if coupon is not None:
            self.button__save.setEnabled(True)
            self.coupon = coupon
            self.name_input.setText(coupon.full_name)
            self.national_input.setText(coupon.national_code)
            self.personnel_input.setText(coupon.personnel_code)
            if coupon.expired_time >= today:
                d_from, d_to = get_this_month_first_and_last_day(gregorian=True)
                used_coupons = self.session.query(UsedCoupon).filter(
                    UsedCoupon.coupon_id == coupon.id, UsedCoupon.use_time.between(d_from, d_to)
                )
                if len(list(used_coupons)) >= coupon.use_limit:
                    self.result.setText('دفعات مجاز استفاده از کد سپری شده است')
                    self.button__submit.setEnabled(False)
                    self.result_icon.load('assets/failed.png')
                else:
                    self.result.setText('کد معتبر')
                    self.result_icon.load('assets/successful.png')
                    self.button__submit.setEnabled(True)


            else:
                self.result.setText('تاریخ انقضای کد سپری شده است')
                self.button__submit.setEnabled(False)
                self.result_icon.load('assets/failed.png')
        else:
            self.result.setText('کد نامعتبر')
            self.button__submit.setEnabled(False)
            self.result_icon.load('assets/failed.png')
        self.label2.setPixmap(self.result_icon)

        self.use_model.removeRows(0, self.use_model.rowCount())
        for used_coupon in used_coupons:
            jdate = date2jalali(used_coupon.use_time)
            items = [QStandardItem(used_coupon.use_time.strftime("%H:%M")),
                     QStandardItem(jdate.strftime("%Y/%m/%d")),
                     QStandardItem(jdate.strftime("%A"))]
            self.use_model.appendRow(items)

    def save_info(self):
        try:
            int(self.national_input.text())
            int(self.personnel_input.text())
        except ValueError:
            QMessageBox.information(self, "Error", "کدملی و شماره پرسنلی باید عددی باشند")
            return
        coupon = self.session.query(Coupon).filter(Coupon.code == self.coupon.code).first()
        coupon.full_name = self.name_input.text()
        coupon.national_code = self.national_input.text()
        coupon.personnel_code = self.personnel_input.text()
        self.session.add(coupon)
        self.session.commit()

        QMessageBox.information(self, "Ok", "با موفقیت ثبت شد.")
        self.button__save.setEnabled(False)

    def submit(self):
        if self.coupon is not None:
            used_coupon = UsedCoupon(coupon=self.coupon)
            jdate = date2jalali(used_coupon.use_time)
            self.session.add(used_coupon)
            self.session.commit()
            self.coupon = None
            self.code.setText('')
            QMessageBox.information(self, "Ok", "با موفقیت ثبت شد.")
            items = [QStandardItem(used_coupon.use_time.strftime("%H:%M")),
                     QStandardItem(jdate.strftime("%Y/%m/%d")),
                     QStandardItem(jdate.strftime("%A"))]
            self.use_model.appendRow(items)

        self.button__submit.setEnabled(False)
        self.result.setText('')
        self.result_icon.load('')
        self.label2.setPixmap(self.result_icon)

        self.button__save.setEnabled(False)


    def add_coupon(self):
        codes = []
        if validate_jalali_date_format(self.coupon_expire_input.text()):
            count = int(self.coupon_count_input.text())
            raw_jdate = list(map(int, self.coupon_expire_input.text().split('/')))
            use_limit = int(self.coupon_use_limit_input.text())
            expire_date = jdatetime.date(year=raw_jdate[0], month=raw_jdate[1], day=raw_jdate[2]).togregorian()
            for i in range(count):
                coupon = Coupon(expired_time=expire_date, use_limit=use_limit)
                if coupon.code not in codes and self.session.query(Coupon).filter(Coupon.code == coupon.code).first() is None:
                    codes.append(coupon.code)
                    self.session.add(coupon)
            self.session.commit()
            save_to_excel(codes)
            QMessageBox.information(self, "Ok", "با موفقیت ثبت شد.")
            self.load_coupons()
        else:
            QMessageBox.critical(self, "خطا", "فرمت تاریخ اشتباه است!")


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.setLayoutDirection(QtCore.Qt.RightToLeft)
    window.show()
    app.exec_()
