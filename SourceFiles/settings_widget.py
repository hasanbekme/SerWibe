import win32print
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget

from utils.printer import get_printers
from utils.system_settings import Settings
from Resources.ui import settings_widget


class SettingsWidget(QWidget, settings_widget.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.settings = Settings()
        self.startup_settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                                          QSettings.NativeFormat)
        self.cancel_button.clicked.connect(self.hide)
        self.accept_button.clicked.connect(self.save)

    def update_data(self):
        if self.startup_settings.value("SerWibe", type=str) != "":
            self.autostart.setChecked(True)
        else:
            self.autostart.setChecked(False)
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
