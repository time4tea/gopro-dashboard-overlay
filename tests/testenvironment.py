import os


def is_ci():
    return os.environ.get("CI") is not None


def is_make():
    return is_ci() or os.environ.get("TEST") is not None
