# Adding item on the menu bar
import sys

from PyQt5.QtCore import QSettings

import res_rc
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from SourceFiles.settings_widget import SettingsWidget


class MyTray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.s_w = None
        self.setIcon(QIcon(":/main/logo.png"))
        self.menu = QMenu()
        self.settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                                  QSettings.NativeFormat)

        self.stop_action = QAction("Stop server")
        self.stop_action.setIcon(QIcon(":/main/stop_icon.png"))
        self.open_action = QAction("Open")
        self.open_action.setIcon(QIcon(":/main/open_icon.png"))
        self.open_settings = QAction("Settings")
        self.open_settings.setIcon(QIcon(":/main/settings.png"))
        self.autostart = QAction("Autostart", self, checkable=True)
        if self.settings.value("SerWibe", type=str) != "":
            self.autostart.setChecked(True)
        else:
            self.autostart.setChecked(False)

        self.menu.addAction(self.open_action)
        self.menu.addAction(self.open_settings)
        self.menu.addAction(self.autostart)
        self.menu.addAction(self.stop_action)

        self.open_settings.triggered.connect(self.open_settings_widget)
        self.setContextMenu(self.menu)

    def open_settings_widget(self):
        self.s_w = SettingsWidget()
        self.s_w.show()
