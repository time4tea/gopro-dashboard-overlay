import pytest

from gopro_overlay.arguments import gopro_dashboard_arguments


def test_input_output():
    assert do_args(input="input").input == "input"
    assert do_args(output="output").output == "output"


def test_overlay_only():
    assert do_args().generate == "default"
    assert do_args("--generate", "overlay").generate == "overlay"
    assert do_args("--generate", "none").generate == "none"


def test_show_ffmpeg():
    assert do_args().show_ffmpeg is False
    assert do_args("--show-ffmpeg").show_ffmpeg is True


def test_debug_metadata():
    assert do_args().debug_metadata is False
    assert do_args("--debug-metadata").debug_metadata is True


def test_overlay_size():
    assert do_args("--overlay-size", "320x256").overlay_size == "320x256"


def test_layout():
    assert do_args().layout == "default"
    assert do_args("--layout", "speed-awareness").layout == "speed-awareness"
    assert do_args("--layout", "xml").layout == "xml"
    with pytest.raises(SystemExit):
        assert do_args("--layout", "bob").layout == "xml"


def test_font():
    assert do_args().font == "Roboto-Medium.ttf"
    assert do_args("--font", "Bob.ttf").font == "Bob.ttf"


def test_fork():
    assert not do_args().fork
    assert do_args("--fork").font


def test_include():
    assert do_args().include is None
    assert do_args("--include", "something").include == ["something"]
    assert do_args("--include", "something", "else").include == ["something", "else"]


def test_exclude():
    assert do_args().exclude is None
    assert do_args("--exclude", "something").exclude == ["something"]
    assert do_args("--exclude", "something", "else").exclude == ["something", "else"]


def do_args(*args, input="input", output="output"):
    all_args = [input, output, *args]
    print(all_args)
    return gopro_dashboard_arguments(all_args)
