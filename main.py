import sys

import django
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from SourceFiles.tray_icon import MyTray
from utils.activation import LicenseInfo
from utils.core import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SerWibe.settings')
django.setup()
current_path = os.getcwd()
strartup_settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                              QSettings.NativeFormat)


def set_autostart(state):
    if state:
        strartup_settings.setValue("SerWibe", sys.argv[0])
    else:
        strartup_settings.remove("SerWibe")


if __name__ == '__main__':
    try:
        if check_running_server():
            pass
        else:
            app = QApplication(sys.argv)
            tray_icon = MyTray()
            tray_icon.server = Thread(target=run_server, args=[], daemon=True)
            tray_icon.stop_action.triggered.connect(app.quit)
            tray_icon.stop_action.triggered.connect(tray_icon.server.stop)
            tray_icon.s_w.autostart.stateChanged.connect(set_autostart)
            if tray_icon.license.is_allowed_today():
                tray_icon.license.create_license(start_date=datetime.today(), end_date=tray_icon.license.end_date)
                tray_icon.server.start()
                tray_icon.open_app()
            else:
                tray_icon.s_w.show()
                tray_icon.s_w.tab.setCurrentIndex(2)
            tray_icon.setVisible(True)
            sys.exit(app.exec())
    except Exception as ex:
        logging.error(ex)
