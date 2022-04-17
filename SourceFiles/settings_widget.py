from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget
from utils.system_settings import Settings
from Resources.ui import settings_widget


class SettingsWidget(QWidget, settings_widget.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.settings = Settings()
        self.cancel_button.clicked.connect(self.hide)
        self.accept_button.clicked.connect(self.save)

    def update_data(self):
        self.company_name_edit.setText(self.settings.get(key="company_name", tp=str))
        self.address_edit.setText(self.settings.get(key="address", tp=str))
        self.number_edit.setText(self.settings.get(key="phone_number", tp=str))
        self.last_message_edit.setText(self.settings.get(key="last_message", tp=str))
        self.tax_edit.setValue(self.settings.get(key="tax", tp=int))

    def save(self):
        self.settings.set(key="company_name", value=self.company_name_edit.text())
        self.settings.set(key="address", value=self.address_edit.text())
        self.settings.set(key="phone_number", value=self.number_edit.text())
        self.settings.set(key="last_message", value=self.last_message_edit.text())
        self.settings.set(key="tax", value=self.tax_edit.value())
        self.hide()
        
    def show(self) -> None:
        self.update_data()
        super(SettingsWidget, self).show()

    def closeEvent(self, e: QCloseEvent):
        e.ignore()
        self.hide()
