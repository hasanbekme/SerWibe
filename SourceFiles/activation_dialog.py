import datetime

import clipboard
from PyQt5.QtWidgets import QDialog, QMessageBox
from future.backports.datetime import timedelta

from Resources.ui import activation_dialog
from utils.activation import LicenseInfo
from utils.cryptography import CryptoGraphy, encode_string
from web.context_pro import _


class ActivationDialog(QDialog, activation_dialog.Ui_Dialog):
    def __init__(self, license_info, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.license: LicenseInfo = license_info
        self.cryptography = CryptoGraphy()
        self.given_text.setReadOnly(True)
        self.start_date.dateChanged.connect(self.balance_dates)
        self.ok_button.clicked.connect(self.generate_activation_string)
        self.copy_button.pressed.connect(self.copy_string)
        self.paste_button.pressed.connect(self.paste_key)
        self.activate_button.pressed.connect(self.process_activation)
        self.encoded_text.textChanged.connect(self.check_input)
        self.translate_ui()

    def translate_ui(self):
        self.title.setText(_('ac_1'))
        self.activate_button.setText(_('ac_2'))
        if self.license.has_license:
            self.start_date.setDate(self.license.end_date + timedelta(days=1))
            self.start_date.setEnabled(False)
            self.end_date.setMinimumDate(self.start_date.date().toPyDate() + timedelta(days=6))
        else:
            self.start_date.setMinimumDate(datetime.datetime.today())
            self.end_date.setMinimumDate(datetime.datetime.today() + timedelta(days=6))

    def check_input(self):
        if self.encoded_text.text() != "":
            self.start_date.setEnabled(False)
            self.end_date.setEnabled(False)
            self.ok_button.setEnabled(False)
        else:
            self.start_date.setEnabled(True)
            self.end_date.setEnabled(True)
            self.ok_button.setEnabled(True)

    def copy_string(self):
        clipboard.copy(self.given_text.text())

    def paste_key(self):
        self.encoded_text.setText(clipboard.paste())

    def balance_dates(self):
        self.given_text.setText("")
        self.encoded_text.setText("")
        self.end_date.setMinimumDate(self.start_date.date().toPyDate() + timedelta(days=6))
        self.end_date.setDate(self.start_date.date().toPyDate() + timedelta(days=6))

    def generate_activation_string(self):
        activation_string = self.license.make_license_text(self.start_date.date().toPyDate(),
                                                           self.end_date.date().toPyDate())
        self.given_text.setText(self.cryptography.encrypt(activation_string))

    def process_activation(self):
        if self.encoded_text.text() == encode_string(self.given_text.text()) and self.given_text.text() != "":
            if self.license.has_license:
                self.license.create_license(self.license.start_date, self.end_date.date().toPyDate())
            else:
                self.license.create_license(self.start_date.date().toPyDate(), self.end_date.date().toPyDate())
            msg_success = QMessageBox()
            msg_success.setIcon(QMessageBox.Information)
            msg_success.setText(_('ac_9'))
            msg_success.setWindowTitle(_('ac_1'))
            msg_success.setStandardButtons(QMessageBox.Ok)
            msg_success.exec_()
            self.accept()
        else:
            msg_error = QMessageBox()
            msg_error.setIcon(QMessageBox.Critical)
            msg_error.setText(_('ac_10'))
            msg_error.setWindowTitle(_('ac_1'))
            msg_error.setStandardButtons(QMessageBox.Ok)
            msg_error.exec_()
