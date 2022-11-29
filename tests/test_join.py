import contextlib
import os
import tempfile
from os import chdir
from pathlib import Path

from gopro_overlay.filenaming import GoProFile, Encoding


def test_gopro_file_naming_avc():
    f = GoProFile(Path("GH010072.MP4"))
    assert f.name == "GH010072.MP4"
    assert f.letter == "H"
    assert f.encoding == Encoding.AVC
    assert f.recording == 72
    assert f.sequence == 1


def test_gopro_file_naming_hevc():
    f = GoProFile(Path("GX971029.MP4"))
    assert f.name == "GX971029.MP4"
    assert f.letter == "X"
    assert f.encoding == Encoding.HEVC
    assert f.recording == 1029
    assert f.sequence == 97


files = [
    "GH010072.MP4", "GH020072.MP4", "GH030072.MP4", "GH040072.MP4",
    "GH010172.MP4", "GH020172.MP4", "GH030172.MP4", "GH040172.MP4",
]


def test_finding_files_belonging_to():
    f = GoProFile(Path("GH010072.MP4"))
    found = f.related_files(Path("/some/dir"), listdir=lambda d: files)

    assert len(found) == 4
    assert found[0].name == "GH010072.MP4"
    assert found[3].name == "GH040072.MP4"


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
            related = gpf.related_files(td)
            names = [r.name for r in related]
            assert names == ['GH010072.MP4', 'GH020072.MP4', 'GH030072.MP4', 'GH040072.MP4']


def test_real_directory_current_dir():
    with tempfile.TemporaryDirectory() as td:
        for f in files:
            (Path(td) / f).write_text("content")

        with working_directory(td):
            gpf = GoProFile(Path("GH020072.MP4"))
            related = gpf.related_files(".")
            names = [r.name for r in related]
            assert names == ['GH010072.MP4', 'GH020072.MP4', 'GH030072.MP4', 'GH040072.MP4']
