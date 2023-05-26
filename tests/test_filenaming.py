from pathlib import Path

import pytest

from gopro_overlay.filenaming import GoProFile, Encoding

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


hero5_files = [
    "GP011234.mp4", "GP021234.mp4"
]


def test_finding_files_belonging_to_hero5():
    f = GoProFile(Path("GP011234.mp4"))
    found = f.related_files(Path("/some/dir"), listdir=lambda d: hero5_files)

    assert len(found) == 2
    assert found[0].name == "GP011234.mp4"
    assert found[1].name == "GP021234.mp4"


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


def test_gopro_file_naming_hero5_single():
    f = GoProFile(Path("GOPR1234.mp4"))
    assert f.name == "GOPR1234.mp4"
    assert f.letter == "OPR"
    assert f.encoding == Encoding.AVC
    assert f.recording == 1234
    assert f.sequence == 0


def test_gopro_file_naming_hero5_chapters():
    f = GoProFile(Path("GP011234.mp4"))
    assert f.name == "GP011234.mp4"
    assert f.letter == "P"
    assert f.encoding == Encoding.AVC
    assert f.recording == 1234
    assert f.sequence == 1


def test_renamed_files():
    with pytest.raises(ValueError):
        GoProFile(Path("1.1-GX010092.MP4"))

    with pytest.raises(ValueError):
        GoProFile(Path("bob/1.1-GX010092.MP4"))
