import os
import shutil

import django
from django.db.models import Sum

from SourceFiles.activation_dialog import ActivationDialog
from utils.activation import LicenseInfo
from web.context_pro import _, languages, get_lang_code

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SerWibe.settings')
django.setup()

from utils.payment_receipt import print_receipt_test
from web.models import Order
import webbrowser
from datetime import datetime

import win32print
from PyQt5.QtCore import QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog

from Resources.ui import settings_widget
from utils.bot_config import logs_channel, bot
from utils.core import get_env, thd_sp
from utils.excel import export_archive_data
from utils.printer import get_printers
from utils.system_settings import Settings


class LogsThread(QThread):
    error_msg = pyqtSignal()

    def run(self):
        try:
            todays_log = get_env() + "\\" + datetime.today().strftime("logs_%d-%m-%Y.log")
            doc = open(todays_log, 'r+')
            text = doc.readlines()
            if len(text) == 0:
                doc.write("No logs yet")
            doc.close()
            doc = open(todays_log, 'r')
            settings = Settings()
            license_info = LicenseInfo()
            log_caption = "\n".join([
                f"#logs <b>{datetime.today().strftime('%d/%M/%Y %H:%M')}</b>",
                f"#{settings.get('admin_id', str)}",
                f"#{license_info.product_id}",
                f"<b>Start Date:</b> {license_info.start_date.strftime('%d/%m/%Y')}",
                f"<b>End Date:</b> {license_info.end_date.strftime('%d/%m/%Y')}",
                f"<b>Company Name:</b> {settings.get('company_name', str)}",
                f"<b>Phone Number:</b> {settings.get('phone_number', str)}",
                f"<b>Address:</b> {settings.get('address', str)}",
            ])
            bot.send_document(logs_channel, doc, caption=log_caption)
        except:
            self.error_msg.emit()


class ReportThread(QThread):
    error_msg = pyqtSignal()

    def run(self):
        try:
            report_doc = open(get_env() + "\\" + export_archive_data(start_date='today'), 'rb')
            today = datetime.today()
            completed_orders = Order.objects.filter(is_completed=True, created_at__year=today.year,
                                                    created_at__month=today.month, created_at__day=today.day)
            cash_money = completed_orders.aggregate(Sum('cash_money'))['cash_money__sum']
            if cash_money is None:
                cash_money = 0
            credit_card = completed_orders.aggregate(Sum('credit_card'))['credit_card__sum']
            if credit_card is None:
                credit_card = 0
            debt_money = completed_orders.aggregate(Sum('debt_money'))['debt_money__sum']
            if debt_money is None:
                debt_money = 0
            total_flow = cash_money + credit_card + debt_money
            if total_flow != 0:
                cash_p = int(cash_money / total_flow * 100)
                credit_card_p = int(credit_card / total_flow * 100)
                debt_money_p = 100 - (cash_p + credit_card_p)
            else:
                cash_p = 0
                credit_card_p = 0
                debt_money_p = 0
            doc_caption = f"💴 ({cash_p}%) {thd_sp(cash_money)} {_('r_8')}\n" \
                          f"💳 ({credit_card_p}%) {thd_sp(credit_card)} {_('r_8')}\n" \
                          f"🚫 ({debt_money_p}%) {thd_sp(debt_money)} {_('r_8')}"
            bot.send_document(chat_id=Settings().get(key='admin_id', tp=int), document=report_doc, caption=doc_caption)
        except Exception as er:
            print(er)
            self.error_msg.emit()


def open_id_bot():
    webbrowser.open(url="https://t.me/my_id_bot")


class SettingsWidget(QWidget, settings_widget.Ui_Form):
    check_license_signal = pyqtSignal(LicenseInfo)

    def __init__(self, license_info):
        super().__init__()
        self.setupUi(self)
        self.license: LicenseInfo = license_info
        self.translate_ui()
        self.settings = Settings()
        self.startup_settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                                          QSettings.NativeFormat)
        self.cancel_button.clicked.connect(self.hide)
        self.accept_button.clicked.connect(self.save)
        self.language_box.currentTextChanged.connect(self.change_language)
        self.send_logs.clicked.connect(self.send_logs_func)
        self.admin_report.clicked.connect(self.send_admin_report)
        self.id_bot.clicked.connect(open_id_bot)
        self.admin_id_edit.textChanged.connect(self.admin_id_changed)
        self.new_license_btn.pressed.connect(self.add_activation)
        self.open_from_browser.stateChanged.connect(self.open_setting_changed)
        self.clear_database_btn.clicked.connect(self.clear_database)
        self.open_folder.clicked.connect(self.changeDefaultPath)
        self.has_name.stateChanged.connect(self.change_checkbox_states)
        self.has_logo.stateChanged.connect(self.change_checkbox_states)
        self.test_print.clicked.connect(self.test_receipt)
        self.access_to_waiter.stateChanged.connect(
            lambda x: self.settings.set(key="access_to_waiter", value=self.access_to_waiter.isChecked()))

    def translate_ui(self):
        self.setWindowTitle(_('s_0'))
        self.tab.setTabText(0, _('s_1'))
        self.tab.setTabText(1, _('s_2'))
        self.tab.setTabText(2, _('s_3'))
        self.title_2.setText(_('s_4'))
        self.autostart_title.setText(_('s_5'))
        self.language_title.setText(_('s_6'))
        self.label.setText(_('s_7'))
        self.admin_report.setText(_('s_8'))
        self.send_logs.setText(_('s_9'))
        self.title.setText(_('s_10'))
        self.company_name.setText(_('s_11'))
        self.address_label.setText(_('s_12'))
        self.number_label.setText(_('s_13'))
        self.tax_label.setText(_('s_14'))
        self.last_message_label.setText(_('s_15'))
        self.cash_register.setText(_('s_16'))
        self.printer_size_label.setText(_('s_17'))
        self.cancel_button.setText(_('s_18'))
        self.accept_button.setText(_('s_19'))
        self.open_from_browser_label.setText(_('s_20'))
        self.current_status_msg.setText(_('ac_3'))
        self.license_status.setText(_('ac_4'))
        self.label_4.setText(_('ac_7'))
        self.new_license_btn.setText(_('ac_8'))
        self.clear_database_btn.setText(_('s_22'))
        self.waiter_access_label.setText(_('s_26'))
        self.logo_title.setText(_('s_25'))
        self.test_print.setText(_('s_30'))
        self.check_license()

    def test_receipt(self):
        print_receipt_test(self.has_logo.isChecked(), self.default_path.text(), self.has_name.isChecked(),
                           self.company_name_edit.text(), self.address_edit.text(), self.number_edit.text(),
                           self.tax_edit.value(), self.last_message_edit.text(), self.printer.currentText(),
                           self.printer_width_edit.value())

    def clear_database(self):
        alert_dialog = QMessageBox()
        alert_dialog.setIcon(QMessageBox.Question)
        alert_dialog.setText(_('s_23'))
        alert_dialog.setWindowTitle(_('s_22'))
        alert_dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        returnValue = alert_dialog.exec()
        if returnValue == QMessageBox.Ok:
            Order.objects.filter(is_completed=True).delete()

    def add_activation(self):
        self.activation_frame = ActivationDialog(self.license, self)
        self.activation_frame.accepted.connect(self.update_license_info)
        self.activation_frame.exec_()

    def update_license_info(self):
        self.license = LicenseInfo()
        self.translate_ui()
        self.check_license_signal.emit(self.license)

    def check_license(self):
        if self.license.is_allowed_today():
            self.license_status.setText(_('ac_4'))
            self.license_status.setStyleSheet("QLabel {color : green; }")
            self.license_status_icon.setIcon(QIcon(":/main/unlocked.png"))
            self.remaining_days.setText(f"{(self.license.end_date - datetime.today()).days + 1} {_('ac_6')}")
            self.start_date.setDate(self.license.start_date)
            self.start_date.setReadOnly(True)
            self.end_date.setDate(self.license.end_date)
            self.end_date.setReadOnly(True)
            self.remaining_days.setVisible(True)
            self.license_info.setVisible(True)
        else:
            self.license_status.setStyleSheet("QLabel {color : red; }")
            self.license_status_icon.setIcon(QIcon(":/main/locked.png"))
            self.license_status.setText(_('ac_5'))
            self.license_info.setVisible(False)
            self.remaining_days.setVisible(False)

    def change_checkbox_states(self):
        state_logo = self.has_logo.isChecked()
        self.default_path.setEnabled(state_logo)
        self.open_folder.setEnabled(state_logo)

        self.company_name_edit.setEnabled(self.has_name.isChecked())

    def send_admin_report(self):
        self.report_thread = ReportThread()
        self.report_thread.error_msg.connect(self.connection_error)
        self.report_thread.start()

    def send_logs_func(self):
        self.logs_thread = LogsThread()
        self.logs_thread.error_msg.connect(self.connection_error)
        self.logs_thread.start()

    def connection_error(self):
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Critical)
        mb.setText(_('s_21'))
        mb.setWindowTitle("Error")
        mb.setStandardButtons(QMessageBox.Ok)
        mb.exec_()

    def admin_id_changed(self):
        self.settings.set(key='admin_id', value=self.admin_id_edit.text())

    def open_setting_changed(self):
        self.settings.set(key='open_from_browser', value=self.open_from_browser.isChecked())

    def change_language(self):
        self.settings.set(key='lang_code', value=get_lang_code(self.language_box.currentText()))
        self.translate_ui()

    def update_data(self):
        if self.startup_settings.value("SerWibe", type=str) != "":
            self.autostart.setChecked(True)
        else:
            self.autostart.setChecked(False)
        self.open_from_browser.setChecked(self.settings.get(key='open_from_browser', tp=bool))
        self.access_to_waiter.setChecked(self.settings.get(key='access_to_waiter', tp=bool))
        lang_code = self.settings.get(key='lang_code', tp=str)
        if lang_code is "":
            lang_code = 'uz'
        self.language_box.setCurrentText(languages[lang_code])
        self.admin_id_edit.setText(self.settings.get(key="admin_id", tp=str))
        if self.settings.get(key="has_company_logo", tp=bool):
            self.has_logo.setChecked(True)
            self.default_path.setText(self.settings.get(key='company_logo', tp=str))
        else:
            self.default_path.setEnabled(False)
            self.open_folder.setEnabled(False)
        if self.settings.get(key="has_company_name", tp=bool):
            self.has_name.setChecked(True)
            self.company_name_edit.setText(self.settings.get(key="company_name", tp=str))
        else:
            self.company_name_edit.setEnabled(False)
        self.address_edit.setText(self.settings.get(key="address", tp=str))
        self.number_edit.setText(self.settings.get(key="phone_number", tp=str))
        self.last_message_edit.setText(self.settings.get(key="last_message", tp=str))
        self.tax_edit.setValue(self.settings.get(key="tax", tp=int))
        printers = get_printers()
        self.printer.clear()
        for i in printers:
            self.printer.addItem(i)
        current_printer = self.settings.get(key='printer', tp=str)
        if current_printer != "" and current_printer in printers:
            self.printer.setCurrentText(current_printer)
        else:
            current_printer = win32print.GetDefaultPrinter()
            self.printer.setCurrentText(current_printer)
            self.settings.set('printer', current_printer)
        self.printer_width_edit.setValue(self.settings.get(key="printer_width", tp=int))

    def save(self):
        print("saving")
        if self.has_logo.isChecked():
            if self.default_path.text() != "":
                self.settings.set(key="has_company_logo", value=True)
                self.settings.set(key="company_logo", value=self.default_path.text())
                try:
                    shutil.copy(self.default_path.text(),
                                get_env() + f"\\company_logo.{self.default_path.text().split('.')[-1]}")
                except:
                    QMessageBox.critical(self, _('s_9'), _('s_29'))
                    return
            else:
                QMessageBox.critical(self, _('s_9'), _('s_27'))
                return
        else:
            self.settings.set(key="has_company_logo", value=False)
            self.settings.set(key="company_logo", value="")
        if self.has_name.isChecked():
            if self.company_name_edit.text() != "":
                self.settings.set(key="has_company_name", value=True)
                self.settings.set(key="company_name", value=self.company_name_edit.text())
            else:
                QMessageBox.critical(self, _('s_9'), _('s_28'))
                return
        else:
            self.settings.set(key="has_company_name", value=False)
            self.settings.set(key="company_name", value="")
        self.settings.set(key="company_name", value=self.company_name_edit.text())
        self.settings.set(key="address", value=self.address_edit.text())
        self.settings.set(key="phone_number", value=self.number_edit.text())
        self.settings.set(key="last_message", value=self.last_message_edit.text())
        self.settings.set(key="tax", value=self.tax_edit.value())
        self.settings.set(key="printer", value=self.printer.currentText())
        self.settings.set(key="printer_width", value=self.printer_width_edit.value())
        print("ok")
        self.hide()

    def changeDefaultPath(self):
        self.save_dir = QFileDialog.getOpenFileName(self, "Select logo", './', 'Images (*.png *.jpg)')
        print(self.save_dir)
        if self.save_dir[0] != "":
            self.default_path.setText(self.save_dir[0])

    def show(self) -> None:
        self.update_data()
        super(SettingsWidget, self).show()

    def closeEvent(self, e: QCloseEvent):
        e.ignore()
        self.tab.setCurrentIndex(0)
        self.hide()
