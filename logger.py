import os
import tempfile

from gi.repository import Gimp

from config import PLUGIN_PROC


LOG_FILE = os.path.join(tempfile.gettempdir(), PLUGIN_PROC + ".log")


def log(message: str):
    failed = False

    try:
        Gimp.message(message)
    except Exception:
        failed = True

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(message + "\n")
    except Exception:
        failed = True

    if failed:
        print(message)
