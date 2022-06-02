# Adding item on the menu bar

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction

from SourceFiles.main_window import MainWindow
from SourceFiles.settings_widget import SettingsWidget
from utils.activation import LicenseInfo


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
        self.settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                                  QSettings.NativeFormat)

        self.stop_action = QAction("Stop server")
        self.stop_action.setIcon(QIcon(":/main/stop_icon.png"))
        self.open_settings = QAction("Settings")
        self.open_settings.setIcon(QIcon(":/main/settings.png"))

        self.menu.addAction(self.open_settings)
        self.menu.addAction(self.stop_action)

        self.open_settings.triggered.connect(self.open_settings_widget)
        self.setContextMenu(self.menu)

    def check_license(self, info: LicenseInfo):
        self.license = info

        if not self.server.is_alive() and self.license.is_allowed_today():
            self.server.start()
            self.main_frame.showMaximized()
            self.main_frame.browser.reload()
            self.s_w.close()

    def open_settings_widget(self):
        self.s_w.show()
