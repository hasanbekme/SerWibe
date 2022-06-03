import os

import django

from SourceFiles.activation_dialog import ActivationDialog
from utils.activation import LicenseInfo
from web.context_pro import _, languages, get_lang_code

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SerWibe.settings')
django.setup()

from web.models import Order
import webbrowser
from datetime import datetime

import win32print
from PyQt5.QtCore import QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QWidget, QMessageBox

from Resources.ui import settings_widget
from utils.bot_config import logs_channel, bot
from utils.core import get_env
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
            bot.send_document(logs_channel, doc, caption=f"#logs <b>{datetime.today().strftime('%d/%M/%Y %H:%M')}</b>")
        except:
            self.error_msg.emit()


class ReportThread(QThread):
    error_msg = pyqtSignal()

    def run(self):
        try:
            report_doc = open(get_env() + "\\" + export_archive_data(start_date='today'), 'rb')
            bot.send_document(chat_id=Settings().get(key='admin_id', tp=int), document=report_doc)
        except:
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

    def translate_ui(self):
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
        self.check_license()

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
        lang_code = self.settings.get(key='lang_code', tp=str)
        if lang_code is "":
            lang_code = 'uz'
        self.language_box.setCurrentText(languages[lang_code])
        self.admin_id_edit.setText(self.settings.get(key="admin_id", tp=str))
        self.company_name_edit.setText(self.settings.get(key="company_name", tp=str))
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
        self.settings.set(key="company_name", value=self.company_name_edit.text())
        self.settings.set(key="address", value=self.address_edit.text())
        self.settings.set(key="phone_number", value=self.number_edit.text())
        self.settings.set(key="last_message", value=self.last_message_edit.text())
        self.settings.set(key="tax", value=self.tax_edit.value())
        self.settings.set(key="printer", value=self.printer.currentText())
        self.settings.set(key="printer_width", value=self.printer_width_edit.value())
        self.hide()

    def show(self) -> None:
        self.update_data()
        super(SettingsWidget, self).show()

    def closeEvent(self, e: QCloseEvent):
        e.ignore()
        self.tab.setCurrentIndex(0)
        self.hide()
