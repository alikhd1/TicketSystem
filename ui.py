from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QListWidget, QListWidgetItem, QMessageBox, QTableView, QMainWindow
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from models import Coupon, UsedCoupon
from utils.date import get_this_month_first_and_last_day, date2jalali


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the database connection
        self.coupon = None
        engine = create_engine('sqlite:///data.db')
        Session = sessionmaker(bind=engine)
        self.session = Session()

        self.label1 = QtWidgets.QLabel('کد')
        self.code = QtWidgets.QLineEdit()

        self.button__check = QPushButton('بررسی', self)
        self.button__check.clicked.connect(self.check_code)

        self.button__submit = QPushButton('ثبت', self)
        self.button__check.clicked.connect(self.submit)

        self.used_coupon_list = QListWidget()
        self.use_table_view = QTableView(self)

        self.use_model = QStandardItemModel(self.use_table_view)
        self.use_model.setHorizontalHeaderLabels(["ساعت", "تاریخ", "روز"])
        self.use_table_view.setModel(self.use_model)

        check_coupons_layout = QtWidgets.QFormLayout()
        check_coupons_layout.addRow(self.label1, self.code)
        check_coupons_layout.addRow(self.button__check)
        check_coupons_layout.addRow(self.button__submit)
        check_coupons_layout.addRow(self.use_table_view)

        # Create the UI elements
        self.coupon_list = QListWidget()
        self.table_view = QTableView(self)

        self.model = QStandardItemModel(self.table_view)
        self.model.setHorizontalHeaderLabels(["Check", "ID", "Code", "Expire Date", "Usage Limit"])
        self.table_view.setModel(self.model)

        self.new_coupon_line_edit = QLineEdit()
        self.new_coupon_button = QPushButton('Add Coupon')
        self.bulk_coupon_line_edit = QLineEdit()
        self.bulk_coupon_button = QPushButton('Add Bulk Coupons')

        # Set up the UI layout
        coupons_layout = QVBoxLayout()
        coupons_layout.addWidget(QLabel('Coupons:'))
        coupons_layout.addWidget(self.table_view)
        add_coupon_layout = QHBoxLayout()
        add_coupon_layout.addWidget(QLabel('New Coupon:'))
        add_coupon_layout.addWidget(self.new_coupon_line_edit)
        add_coupon_layout.addWidget(self.new_coupon_button)
        coupons_layout.addLayout(add_coupon_layout)
        bulk_coupon_layout = QHBoxLayout()
        bulk_coupon_layout.addWidget(QLabel('Bulk Coupons:'))
        bulk_coupon_layout.addWidget(self.bulk_coupon_line_edit)
        bulk_coupon_layout.addWidget(self.bulk_coupon_button)
        coupons_layout.addLayout(bulk_coupon_layout)
        self.setLayout(coupons_layout)

        # Connect the UI signals
        self.new_coupon_button.clicked.connect(self.add_coupon)
        self.bulk_coupon_button.clicked.connect(self.add_bulk_coupons)

        # Load the existing coupons from the database and display them in the UI
        self.load_coupons()

        central_widget = QtWidgets.QTabWidget()

        tab1 = QtWidgets.QWidget()
        tab1.setLayout(check_coupons_layout)
        central_widget.addTab(tab1, "بررسی کوپن")

        tab2 = QtWidgets.QWidget()
        tab2.setLayout(coupons_layout)
        central_widget.addTab(tab2, "کوپن ها")

        # tab3 = QtWidgets.QWidget()
        # tab3.setLayout(check_coupons_layout)
        # central_widget.addTab(tab3, "تنظیمات")

        self.setCentralWidget(central_widget)

    def load_coupons(self):
        self.coupon_list.clear()
        coupons = self.session.query(Coupon).all()
        for coupon in coupons:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckState(Qt.Unchecked)
            checkbox_item.setCheckable(True)

            jdate = date2jalali(coupon.expired_time)

            items = [checkbox_item, QStandardItem(str(coupon.id)), QStandardItem(coupon.code),
                     QStandardItem(jdate.strftime("%Y/%m/%d")), QStandardItem(str(coupon.use_limit))
                     ]
            self.model.appendRow(items)

    def check_code(self):
        import datetime

        code = self.code.text().upper()
        coupon = self.session.query(Coupon).filter(Coupon.code == code).first()
        today = datetime.date.today()
        used_coupons = []
        if coupon is not None:
            if coupon.expired_time >= today:
                d_from, d_to = get_this_month_first_and_last_day(gregorian=True)
                used_coupons = self.session.query(UsedCoupon).filter(
                    UsedCoupon.coupon_id == coupon.id, UsedCoupon.use_time.between(d_from, d_to)
                )
                if len(list(used_coupons)) > coupon.use_limit:
                    QMessageBox.warning(self, "Warning", "دفعات مجاز استفاده از کد سپری شده است.")
                else:
                    QMessageBox.information(self, "Ok", "کد معتبر.")
                    self.coupon = coupon
            else:
                QMessageBox.warning(self, "Warning", "تاریخ انقضای کد سپری شده است.")
        else:
            QMessageBox.warning(self, "Warning", "کد نامعتبر.")

        self.use_model.removeRows(0, self.use_model.rowCount())
        for used_coupon in used_coupons:
            jdate = date2jalali(used_coupon.use_time)
            items = [QStandardItem(used_coupon.use_time.strftime("%H:%M")),
                     QStandardItem(jdate.strftime("%Y/%m/%d")),
                     QStandardItem(jdate.strftime("%A"))]
            self.use_model.appendRow(items)

    def submit(self):
        if self.coupon:
            us = UsedCoupon(coupon=self.coupon)
            self.session.add(us)
            self.session.commit()
        self.coupon = None

    def add_coupon(self):
        # Create a new coupon and add it to the database
        expired_time = date.today()
        coupon = Coupon(expired_time)
        self.session.add(coupon)
        self.session.commit()

        # Update the UI to display the new coupon
        item = QListWidgetItem(str(coupon))
        self.coupon_list.addItem(item)

    def add_bulk_coupons(self):
        # Parse the number of coupons to generate from the UI input
        try:
            count = int(self.bulk_coupon_line_edit.text())
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
            return

        # Generate the new coupons and add them to the database
        expired_time = date.today()
        codes = Coupon.generate_bulk_codes(count)
        for code in codes:
            coupon = Coupon(expired_time, code=code)
            self.session.add(coupon)
        self.session.commit()

        # Update the UI to display the new coupons
        self.load_coupons()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
