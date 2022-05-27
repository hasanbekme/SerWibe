from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow
from Resources.ui import main_window
from utils.core import get_machine_ip


class MainWindow(QMainWindow, main_window.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.load_browser()

    def load_browser(self):
        base_url = f"http://{get_machine_ip()}:9446"

        self.browser.load(QUrl(base_url))

    def showFullScreen(self):
        super(MainWindow, self).showFullScreen()
        self.load_browser()

