import contextlib
import os
import tempfile
from os import chdir
from pathlib import Path

from gopro_overlay.filenaming import GoProFile

files = [
    "GH010072.MP4", "GH020072.MP4", "GH030072.MP4", "GH040072.MP4",
    "GH010172.MP4", "GH020172.MP4", "GH030172.MP4", "GH040172.MP4",
]


@contextlib.contextmanager
def working_directory(directory):
    current = os.getcwd()
    try:
        os.chdir(directory)
        x = yield
        return x
    finally:
        chdir(current)


def test_real_directory():
    with tempfile.TemporaryDirectory() as td:
        for f in files:
            (Path(td) / f).write_text("content")

        with working_directory("/tmp"):
            gpf = GoProFile(Path("GH020072.MP4"))
            related = gpf.related_files(Path(td))
            names = [r.name for r in related]
            assert names == ['GH010072.MP4', 'GH020072.MP4', 'GH030072.MP4', 'GH040072.MP4']


def test_real_directory_current_dir():
    with tempfile.TemporaryDirectory() as td:
        for f in files:
            (Path(td) / f).write_text("content")

        with working_directory(td):
            gpf = GoProFile(Path("GH020072.MP4"))
            related = gpf.related_files(Path("."))
            names = [r.name for r in related]
            assert names == ['GH010072.MP4', 'GH020072.MP4', 'GH030072.MP4', 'GH040072.MP4']
