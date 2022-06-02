# Adding item on the menu bar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from django.conf import Settings

from SourceFiles.main_window import MainWindow
from SourceFiles.settings_widget import SettingsWidget
from utils.activation import LicenseInfo
from utils.core import open_website
from utils.system_settings import Settings


class MyTray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.server = None
        self.license = LicenseInfo()
        self.s_w = SettingsWidget(self.license)
        self.s_w.check_license_signal.connect(self.check_license)
        self.setIcon(QIcon(":/main/logo.png"))
        self.menu = QMenu()
        self.main_frame = MainWindow()
        self.settings = Settings()
        self.stop_action = QAction("Stop server")
        self.stop_action.setIcon(QIcon(":/main/stop_icon.png"))
        self.open_settings = QAction("Settings")
        self.open_settings.setIcon(QIcon(":/main/settings.png"))
        self.open_in_browser = QAction("Open in browser")
        self.open_in_browser.setIcon(QIcon(":/main/open_icon.png"))

        self.menu.addAction(self.open_in_browser)
        self.menu.addAction(self.open_settings)
        self.menu.addAction(self.stop_action)

        self.open_settings.triggered.connect(self.open_settings_widget)
        self.open_in_browser.triggered.connect(self.open_app)
        self.setContextMenu(self.menu)
        self.activated.connect(self.tray_icon_pressed)

    def tray_icon_pressed(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_app()

    def open_app(self):
        self.browser_open = self.settings.get(key='open_from_browser', tp=bool)
        if self.browser_open:
            open_website()
        else:
            self.main_frame.showMaximized()

    def check_license(self, info: LicenseInfo):
        self.license = info

        if not self.server.is_alive() and self.license.is_allowed_today():
            self.server.start()
            self.main_frame.showMaximized()
            self.main_frame.browser.reload()
            self.s_w.close()

    def open_settings_widget(self):
        self.s_w.show()
