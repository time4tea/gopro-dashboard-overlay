import os


def is_ci():
    return os.environ.get("CI") is not None
