import os
import sys

from PyQt5.QtCore import QSettings

import res_rc

import django
from PyQt5.QtWidgets import QApplication

from SourceFiles.tray_icon import MyTray
from utils.core import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SerWibe.settings')
django.setup()
current_path = os.getcwd()
strartup_settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                              QSettings.NativeFormat)


def set_autostart(state):
    print(state)
    if state:
        strartup_settings.setValue("SerWibe", sys.argv[0])
    else:
        strartup_settings.remove("SerWibe")


if __name__ == '__main__':
    try:
        if check_running_server():
            open_website()
        else:
            app = QApplication(sys.argv)

            server = Thread(target=run_server, args=[], daemon=True)
            server.start()

            tray_icon = MyTray()
            tray_icon.setVisible(True)
            tray_icon.stop_action.triggered.connect(app.quit)
            tray_icon.stop_action.triggered.connect(server.stop)
            tray_icon.open_action.triggered.connect(open_website)
            tray_icon.s_w.autostart.stateChanged.connect(set_autostart)

            open_website()
            sys.exit(app.exec())
    except Exception as ex:
        logging.error(ex)
