from gopro_overlay.filenaming import GoProFile, Encoding


def test_gopro_file_naming_avc():
    f = GoProFile("GH010072.MP4")
    assert f.name == "GH010072.MP4"
    assert f.letter == "H"
    assert f.encoding == Encoding.AVC
    assert f.recording == 72
    assert f.sequence == 1


def test_gopro_file_naming_hevc():
    f = GoProFile("GX971029.MP4")
    assert f.name == "GX971029.MP4"
    assert f.letter == "X"
    assert f.encoding == Encoding.HEVC
    assert f.recording == 1029
    assert f.sequence == 97


def test_finding_files_belonging_to():
    files = [
        "GH010072.MP4", "GH020072.MP4", "GH030072.MP4", "GH040072.MP4",
        "GH010172.MP4", "GH020172.MP4", "GH030172.MP4", "GH040172.MP4",
    ]

    f = GoProFile("GH010072.MP4")
    found = f.related_files("/some/dir", listdir=lambda d: files)

    assert len(found) == 4
    assert found[0].name == "GH010072.MP4"
    assert found[3].name == "GH040072.MP4"
