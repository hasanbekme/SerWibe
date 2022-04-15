# Adding item on the menu bar
import res_rc
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction


class MyTray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon(":/main/logo.png"))
        self.menu = QMenu()

        self.stop_action = QAction("Stop server")
        self.stop_action.setIcon(QIcon(":/main/stop_icon.png"))
        self.open_action = QAction("Open")
        self.open_action.setIcon(QIcon(":/main/open_icon.png"))

        self.menu.addAction(self.open_action)
        self.menu.addAction(self.stop_action)
        self.setContextMenu(self.menu)
