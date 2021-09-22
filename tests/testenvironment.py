import os


def is_ci():
    return os.environ.get("DISPLAY") is None
