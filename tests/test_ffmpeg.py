import os
from io import BytesIO
from os import stat_result
from pathlib import Path

import pytest
from PIL import Image

from gopro_overlay import ffmpeg
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg_overlay import FFMPEGOverlay, FFMPEGOptions, FFMPEGOverlayVideo
from gopro_overlay.timeunits import timeunits

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


def test_finding_ffmpeg_version():
    version = ffmpeg.ffmpeg_version(
        invoke=fake_invoke(
            expected=["ffmpeg", "-version"],
            stdout="""ffmpeg version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2000-2021 the FFmpeg developers
built with gcc 11 (Ubuntu 11.2.0-19ubuntu1)
configuration: --prefix=/usr --extra-version=0ubuntu0.22.04.1 --toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu --arch=amd64 --enable-gpl --disable-stripping --enable-gnutls --enable-ladspa --enable-libaom --enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcdio --enable-libcodec2 --enable-libdav1d --enable-libflite --enable-libfontconfig --enable-libfreetype --enable-libfribidi --enable-libgme --enable-libgsm --enable-libjack --enable-libmp3lame --enable-libmysofa --enable-libopenjpeg --enable-libopenmpt --enable-libopus --enable-libpulse --enable-librabbitmq --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libsrt --enable-libssh --enable-libtheora --enable-libtwolame --enable-libvidstab --enable-libvorbis --enable-libvpx --enable-libwebp --enable-libx265 --enable-libxml2 --enable-libxvid --enable-libzimg --enable-libzmq --enable-libzvbi --enable-lv2 --enable-omx --enable-openal --enable-opencl --enable-opengl --enable-sdl2 --enable-pocketsphinx --enable-librsvg --enable-libmfx --enable-libdc1394 --enable-libdrm --enable-libiec61883 --enable-chromaprint --enable-frei0r --enable-libx264 --enable-shared
libavutil      56. 70.100 / 56. 70.100
libavcodec     58.134.100 / 58.134.100
libavformat    58. 76.100 / 58. 76.100
libavdevice    58. 13.100 / 58. 13.100
libavfilter     7.110.100 /  7.110.100
libswscale      5.  9.100 /  5.  9.100
libswresample   3.  9.100 /  3.  9.100
libpostproc    55.  9.100 / 55.  9.100
"""
        )
    )
    assert version == "4.4.2-0ubuntu0.22.04.1"


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

    def stat(file):
        return stat_result([000, 1234, 123, 1, 1000, 1000, 9876, 10, 20, 30])

    streams = ffmpeg.find_recording(
        "whatever",
        invoke=fake_invoke(
            expected=["ffprobe", "-hide_banner", "-print_format", "json", "-show_streams", "whatever"],
            stdout=ffprobe_output
        ),
        find_frame_duration=find_frame,
        stat=stat
    )

    assert streams.video.stream == 0
    assert streams.video.dimension == Dimension(1920, 1080)
    assert streams.video.duration == timeunits(seconds=707.707)
    assert streams.audio.stream == 1
    assert streams.meta.stream == 3
    assert streams.meta.frame_count == 707
    assert streams.meta.timebase == 1000
    assert streams.meta.frame_duration == 1001

    assert streams.file.length == 9876


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

    ffmpeg = FFMPEGOverlay(
        output=Path("output"),
        overlay_size=Dimension(100, 200),
        execution=fake
    )

    with ffmpeg.generate():
        pass

    assert fake.args == [
        "ffmpeg",  #
        '-hide_banner',
        "-y",  # overwrite targets
        '-hide_banner',
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

    ffmpeg = FFMPEGOverlayVideo(input=Path("input"), output=Path("output"), overlay_size=Dimension(3, 4), execution=fake)

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

    ffmpeg = FFMPEGOverlayVideo(input="input", output="output",
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

mydir = Path(os.path.dirname(__file__))
top = mydir.parent
clip = top / "render" / "clip.MP4"

def test_extract_frame():
    if not clip.exists():
        pytest.xfail("Clip doesn't exist - should locally!")

    dimension = ffmpeg.find_recording(clip).video.dimension
    Image.frombytes(mode="RGBA", size=dimension.tuple(), data=ffmpeg.load_frame(clip, timeunits(seconds=2)))




def test_flatten():
    l = ["a", ["b", "c"], "d", ["e", "f", "g"]]
    assert ffmpeg.flatten(l) == ["a", "b", "c", "d", "e", "f", "g"]
