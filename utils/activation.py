import os
from datetime import datetime

from PyQt5.QtCore import QSettings

from utils.core import get_env
from utils.cryptography import decrypt, encrypt

system_settings = QSettings("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
                            QSettings.NativeFormat)
license_path = get_env() + "\\license.bin"
today = datetime.today()


class LicenseInfo:
    def __init__(self):
        if os.path.exists(license_path):
            self.license_file = open(license_path, "rb")
            self.license_data = decrypt(self.license_file.read().decode("utf8"))
            self.license_file.close()
            temp_data = self.license_data.split('_')
            if len(temp_data) == 3 and temp_data[0].isdigit() and temp_data[2].isdigit() and self.check_product_id(
                    temp_data[1]):
                self.has_license = True
                self.product_id = temp_data[1]
                self.start_date = datetime.fromordinal(int(temp_data[0]))
                self.end_date = datetime.fromordinal(int(temp_data[2]))
            else:
                self.has_license = False

        else:
            self.has_license = False

    def check_product_id(self, text):
        if system_settings.value('ProductId', type=str) == text:
            return True
        else:
            return False

    def is_allowed_today(self):
        if self.has_license:
            if self.start_date <= today <= self.end_date:
                return True
            else:
                return False
        else:
            return False

    def make_license_text(self, start_date: datetime, end_date: datetime):
        return f"{start_date.toordinal()}_{system_settings.value('ProductId', type=str)}_{end_date.toordinal()}"

    def create_license(self, start_date: datetime, end_date: datetime):
        license_string = encrypt(
            f"{start_date.toordinal()}_{system_settings.value('ProductId', type=str)}_{end_date.toordinal()}")
        license_file = open(license_path, 'wb')
        license_file.write(license_string.encode("utf8"))
        license_file.close()
