import contextlib
import os
import sys
import tempfile


@contextlib.contextmanager
def smart_open(filename=None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def temp_file_name(**kwargs):
    handle, path = tempfile.mkstemp(**kwargs)
    os.close(handle)
    return path


@contextlib.contextmanager
def temporary_file(**kwargs):
    (fd, name) = tempfile.mkstemp(**kwargs)
    os.close(fd)
    try:
        yield name
    finally:
        os.remove(name)
