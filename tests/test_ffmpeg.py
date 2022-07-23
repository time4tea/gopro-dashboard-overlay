from io import BytesIO
from pathlib import Path

from gopro_overlay import ffmpeg
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGGenerate, FFMPEGRunner, FFMPEGOverlayMulti

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


def test_ffmpeg_generate_execute():
    fake = FFMPEGFake()

    ffmpeg = FFMPEGGenerate(
        output="output",
        overlay_size=Dimension(100, 200),
        runner=fake
    )

    with ffmpeg.generate():
        pass

    assert fake.commands == [
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


class FFMPEGFake(FFMPEGRunner):

    def __init__(self):
        self.commands = None

    def run(self, commands):
        self.commands = commands
        yield BytesIO()

    @property
    def command_line(self):
        return self.commands


def test_ffmpeg_multi():
    runner = FFMPEGFake()
    ff = FFMPEGOverlayMulti(
        runner=runner,
        inputs=["fileA", "fileB", "fileC"],
        output="overlaid",
        overlay_size=Dimension(5, 10)
    )

    with ff.generate():
        pass

    assert runner.command_line == [
        "-y",
        '-hide_banner',
        '-loglevel', 'info',
        "-i", "fileA",
        "-i", "fileB",
        "-i", "fileC",
        "-f", "rawvideo",
        "-framerate", "10.0",
        "-s", "5x10",
        "-pix_fmt", "rgba",
        "-i", "-",
        "-filter_complex", "[0:v][0:a][1:v][1:a][2:v][2:a]concat:n=3:v=1:a=1[vv][a];[vv][3:v]overlay",
        '-vcodec', 'libx264',
        '-preset', 'veryfast',
        "overlaid"
    ]


def test_flatten():
    l = ["a", ["b", "c"], "d", ["e", "f", "g"]]
    assert ffmpeg.flatten(l) == ["a", "b", "c", "d", "e", "f", "g"]
