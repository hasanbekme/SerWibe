from PyQt5.QtCore import QSettings


class Settings:
    def __init__(self):
        self.settings = QSettings('SerWibe', 'Settings')

    def set(self, key: str, value):
        self.settings.setValue(key, value)

    def get(self, key: str, tp: type):
        return self.settings.value(key, type=tp)
