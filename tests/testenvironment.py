import os


def is_ci():
    return os.environ.get("CI") is not None


def is_make():
    get = os.environ.get("TEST")
    print(f"Test is {get}")
    return get is not None
