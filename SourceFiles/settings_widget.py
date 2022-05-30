import os

import django

from web.context_pro import _, languages, get_lang_code

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SerWibe.settings')
django.setup()

import webbrowser
from datetime import datetime

import win32print
from PyQt5.QtCore import QSettings, QThread
from PyQt5.QtGui import QCloseEvent, QMovie, QIcon
from PyQt5.QtWidgets import QWidget

from Resources.ui import settings_widget
from utils.bot_config import logs_channel, bot
from utils.core import get_env
from utils.excel import export_archive_data
from utils.printer import get_printers
from utils.system_settings import Settings


class LogsThread(QThread):
    def run(self):
        doc = open(get_env() + "\\" + datetime.today().strftime("logs_%d-%m-%Y.log"), 'rb')
        bot.send_document(logs_channel, doc, caption=f"#logs <b>{datetime.today().strftime('%d/%M/%Y %H:%M')}</b>")


class ReportThread(QThread):
    def run(self):
        report_doc = open(get_env() + "\\" + export_archive_data(start_date='today'), 'rb')
        bot.send_document(chat_id=Settings().get(key='admin_id', tp=int), document=report_doc)


def open_id_bot():
    webbrowser.open(url="https://t.me/my_id_bot")


class SettingsWidget(QWidget, settings_widget.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.translate_ui()
        self.gif_logs = QMovie(':/main/upload.gif')
        self.gif_admin = QMovie(':/main/upload.gif')
        self.settings = Settings()
        self.startup_settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                                          QSettings.NativeFormat)
        self.cancel_button.clicked.connect(self.hide)
        self.logs_thread = LogsThread()
        self.report_thread = ReportThread()
        self.accept_button.clicked.connect(self.save)
        self.language_box.currentTextChanged.connect(self.change_language)
        self.send_logs.clicked.connect(self.send_logs_func)
        self.admin_report.clicked.connect(self.send_admin_report)
        self.id_bot.clicked.connect(open_id_bot)
        self.admin_id_edit.textChanged.connect(self.admin_id_changed)

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

    def send_logs_func(self):
        self.gif_logs.start()
        self.send_logs.setIcon(QIcon(self.gif_logs.currentPixmap()))
        self.gif_logs.frameChanged.connect(lambda x: self.send_logs.setIcon(QIcon(self.gif_logs.currentPixmap())))
        self.logs_thread.start()
        self.logs_thread.finished.connect(self.stop_sending_logs)

    def send_admin_report(self):
        self.gif_admin.start()
        self.admin_report.setIcon(QIcon(self.gif_admin.currentPixmap()))
        self.gif_logs.frameChanged.connect(lambda x: self.admin_report.setIcon(QIcon(self.gif_admin.currentPixmap())))
        self.report_thread.start()
        self.report_thread.finished.connect(self.stop_sending_report)

    def stop_sending_report(self):
        self.gif_admin.stop()
        self.admin_report.setIcon(QIcon(":/main/submit_document.png"))

    def stop_sending_logs(self):
        self.gif_logs.stop()
        self.send_logs.setIcon(QIcon(":/main/send_logs.png"))

    def admin_id_changed(self):
        self.settings.set(key='admin_id', value=self.admin_id_edit.text())

    def change_language(self):
        self.settings.set(key='lang_code', value=get_lang_code(self.language_box.currentText()))
        self.translate_ui()

    def update_data(self):
        if self.startup_settings.value("SerWibe", type=str) != "":
            self.autostart.setChecked(True)
        else:
            self.autostart.setChecked(False)
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
        self.hide()
