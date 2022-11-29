import contextlib
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional


@contextlib.contextmanager
def smart_open(filepath: Optional[Path] = None):
    if filepath and filepath.name != '-':
        fh = filepath.open("w")
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
