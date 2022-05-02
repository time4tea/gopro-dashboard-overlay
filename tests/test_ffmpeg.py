from io import BytesIO
from pathlib import Path

from gopro_overlay import ffmpeg
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGGenerate, FFMPEGOverlay, FFMPEGOptions

ffprobe_output = (Path(__file__).parent / "test_ffmpeg_ffprobe_output.json").read_text()


class objectview(object):
    def __init__(self, d):
        self.__dict__ = d


def fake_invoke(stderr="", stdout="", expected=None):
    def invoked(commands):
        if expected is not None:
            assert commands == expected

        return objectview({
            "stderr": stderr,
            "stdout": stdout,
        })

    return invoked


def test_parsing_stream_information():
    streams = ffmpeg.find_streams(
        "whatever",
        fake_invoke(
            expected=["ffprobe", "-hide_banner", "-print_format", "json", "-show_streams", "whatever"],
            stdout=ffprobe_output
        )
    )

    assert streams.video == 0
    assert streams.video_dimension == Dimension(1920, 1080)
    assert streams.audio == 1
    assert streams.meta.stream == 3
    assert streams.meta.count == 707
    assert streams.meta.timebase == 1000
    assert streams.meta.frame_duration == 1001


class FakePopen:
    def __init__(self):
        self.stdin = BytesIO()
        self.stdout = BytesIO()
        self.args = None

    def popen(self, cmd, **kwargs):
        self.args = cmd
        return objectview({
            "stdin": self.stdin,
            "stdout": self.stdout,
            "wait": lambda x: None
        })


def test_ffmpeg_generate_execute():
    fake = FakePopen()

    ffmpeg = FFMPEGGenerate(
        output="output",
        overlay_size=Dimension(100, 200),
        popen=fake.popen
    )

    with ffmpeg.generate():
        pass

    assert fake.args == [
        "ffmpeg",  #
        "-y",  # overwrite targets
        "-loglevel", "info",
        "-f", "rawvideo",  # input format 'raw'
        "-framerate", "10.0",  # input framerate
        "-s", "100x200",  # input dimension
        "-pix_fmt", "rgba",  # input pixel format
        "-i", "-",  # input file stdin
        "-r", "30",  # output framerate
        "-vcodec", "libx264",  # output format
        "-preset", "veryfast",  # output quality/encoding preset
        "output"  # output file
    ]


def test_ffmpeg_overlay_execute_default():
    fake = FakePopen()

    ffmpeg = FFMPEGOverlay(input="input", output="output", overlay_size=Dimension(3, 4), popen=fake.popen)

    with ffmpeg.generate():
        pass

    assert fake.args == [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "info",
        "-i", "input",  # input 0
        "-f", "rawvideo",
        "-framerate", "10.0",
        "-s", "3x4",
        "-pix_fmt", "rgba",
        "-i", "-",  # input 1
        "-filter_complex", "[0:v][1:v]overlay",  # overlay input 1 on input 0
        "-vcodec", "libx264",
        "-preset", "veryfast",
        "output"
    ]


def test_ffmpeg_overlay_execute_options():
    fake = FakePopen()

    ffmpeg = FFMPEGOverlay(input="input", output="output",
                           options=FFMPEGOptions(input=["-input-option"], output=["-output-option"]),
                           overlay_size=Dimension(3, 4), popen=fake.popen)

    with ffmpeg.generate():
        pass

    assert fake.args == [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "info",
        "-input-option",  # input option goes before input 0
        "-i", "input",  # input 0
        "-f", "rawvideo",
        "-framerate", "10.0",
        "-s", "3x4",
        "-pix_fmt", "rgba",
        "-i", "-",  # input 1
        "-filter_complex", "[0:v][1:v]overlay",  # overlay input 1 on input 0
        "-output-option",  # output option goes before output
        "output"
    ]


def test_flatten():
    l = ["a", ["b", "c"], "d", ["e", "f", "g"]]
    assert ffmpeg.flatten(l) == ["a", "b", "c", "d", "e", "f", "g"]
