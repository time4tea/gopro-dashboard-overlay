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


def test_finding_frame_duration():
    duration = ffmpeg.find_frame_duration(
        "whatever-file",
        data_stream_number=306,
        invoke=fake_invoke(
            expected=['ffprobe', '-hide_banner', '-print_format', 'json', '-show_packets', '-select_streams', "306",
                      '-read_intervals', '%+#1', 'whatever-file'],
            stdout="""{    "packets": [
        {
            "codec_type": "data",
            "stream_index": 2,
            "pts": 0,
            "pts_time": "0.000000",
            "dts": 0,
            "dts_time": "0.000000",
            "duration": 500,
            "duration_time": "0.033333",
            "size": "1728",
            "pos": "195407",
            "flags": "K_"
        }
    ]
}"""
        )
    )
    assert duration == 500


def test_parsing_stream_information():

    def find_frame(filepath, data_stream, *args):
        assert filepath == "whatever"
        assert data_stream == 3
        return 1001

    streams = ffmpeg.find_streams(
        "whatever",
        invoke=fake_invoke(
            expected=["ffprobe", "-hide_banner", "-print_format", "json", "-show_streams", "whatever"],
            stdout=ffprobe_output
        ),
        find_frame_duration=find_frame
    )

    assert streams.video == 0
    assert streams.video_dimension == Dimension(1920, 1080)
    assert streams.audio == 1
    assert streams.meta.stream == 3
    assert streams.meta.frame_count == 707
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


class FakeExecution:

    def __init__(self):
        self.args = None

    def execute(self, args):
        self.args = args
        yield BytesIO()


def test_ffmpeg_generate_execute():
    fake = FakeExecution()

    ffmpeg = FFMPEGGenerate(
        output="output",
        overlay_size=Dimension(100, 200),
        execution=fake
    )

    with ffmpeg.generate():
        pass

    assert fake.args == [
        "ffmpeg",  #
        '-hide_banner',
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
    fake = FakeExecution()

    ffmpeg = FFMPEGOverlay(input="input", output="output", overlay_size=Dimension(3, 4), execution=fake)

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
    fake = FakeExecution()

    ffmpeg = FFMPEGOverlay(input="input", output="output",
                           options=FFMPEGOptions(input=["-input-option"], output=["-output-option"]),
                           overlay_size=Dimension(3, 4), execution=fake)

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
