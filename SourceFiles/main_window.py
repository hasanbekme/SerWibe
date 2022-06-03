from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from Resources.ui import main_window
from utils.core import get_machine_ip


class MainWindow(QMainWindow, main_window.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.load_browser()
        self.browser.page().profile().downloadRequested.connect(self.on_downloadRequested)

    def on_downloadRequested(self, download):
        old_path = download.url().path()
        suffix = QFileInfo(old_path).suffix()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File", old_path, "*." + suffix
        )
        if path:
            download.setPath(path)
            download.accept()

    def load_browser(self):
        base_url = f"http://{get_machine_ip()}:9446"

        self.browser.load(QUrl(base_url))
