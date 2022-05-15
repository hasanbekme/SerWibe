import logging
import os
import socket
import threading
import webbrowser
from datetime import datetime

import requests


def get_templates_folder():
    return "templates"


def get_media_folder():
    return get_env() + "\\media"


def get_env():
    res = os.getenv("APPDATA") + "\\SerWibe"
    return res


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    filename=get_env() + "\\" + datetime.today().strftime("logs_%d-%m-%Y.log"),
                    level=logging.INFO,
                    )


class Thread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def get_machine_ip():
    return socket.gethostbyname(socket.gethostname())


def check_running_server():
    try:
        requests.get(f"http://{get_machine_ip()}:9446")
        return True
    except:
        return False


def open_website():
    ip_address = get_machine_ip()
    webbrowser.open("http://" + ip_address + ":9446")


def run_server():
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(["manage.py", "runserver", "0.0.0.0:9446", "--noreload"])
    except Exception as exc:
        logging.error(exc)
        return
