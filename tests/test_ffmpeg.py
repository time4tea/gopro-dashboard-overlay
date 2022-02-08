from io import BytesIO

from gopro_overlay import ffmpeg
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGGenerate

ffprobe_output = """[mov,mp4,m4a,3gp,3g2,mj2 @ 0x559b7fad8f00] Using non-standard frame rate 59/1
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'GH010091.MP4':
  Metadata:
    major_brand     : mp41
    minor_version   : 538120216
    compatible_brands: mp41
    creation_time   : 2021-09-29T09:15:49.000000Z
    location        : +0.0-000.0/
    location-eng    : +0.0-000.0/
    firmware        : HD9.01.01.60.00
  Duration: 00:11:47.71, start: 0.000000, bitrate: 45279 kb/s
    Stream #0:0(eng): Video: h264 (High) (avc1 / 0x31637661), yuvj420p(pc, bt709), 1920x1080 [SAR 1:1 DAR 16:9], 45001 kb/s, 59.94 fps, 59.94 tbr, 60k tbn, 119.88 tbc (default)
    Metadata:
      rotate          : 180
      creation_time   : 2021-09-29T09:15:49.000000Z
      handler_name    : GoPro AVC  
      encoder         : GoPro AVC encoder
      timecode        : 09:24:41:04
    Side data:
      displaymatrix: rotation of -180.00 degrees
    Stream #0:1(eng): Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, stereo, fltp, 189 kb/s (default)
    Metadata:
      creation_time   : 2021-09-29T09:15:49.000000Z
      handler_name    : GoPro AAC  
      timecode        : 09:24:41:04
    Stream #0:2(eng): Data: none (tmcd / 0x64636D74) (default)
    Metadata:
      creation_time   : 2021-09-29T09:15:49.000000Z
      handler_name    : GoPro TCD  
      timecode        : 09:24:41:04
    Stream #0:3(eng): Data: bin_data (gpmd / 0x646D7067), 61 kb/s (default)
    Metadata:
      creation_time   : 2021-09-29T09:15:49.000000Z
      handler_name    : GoPro MET  
    Stream #0:4(eng): Data: none (fdsc / 0x63736466), 13 kb/s (default)
    Metadata:
      creation_time   : 2021-09-29T09:15:49.000000Z
      handler_name    : GoPro SOS  
Unsupported codec with id 0 for input stream 2
Unsupported codec with id 100359 for input stream 3
Unsupported codec with id 0 for input stream 4
"""


class objectview(object):
    def __init__(self, d):
        self.__dict__ = d


def fake_invoke(stderr="", stdout=""):
    return lambda x: objectview({
        "stderr": stderr,
        "stdout": stdout,
    })


def test_parsing_stream_information():
    streams = ffmpeg.find_streams("whatever", fake_invoke(stderr=ffprobe_output))

    assert streams.video == 0
    assert streams.video_dimension == Dimension(1920, 1080)
    assert streams.audio == 1
    assert streams.meta == 3


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
        "ffmpeg",                                                    #
        "-y",                                                        # overwrite targets
        "-loglevel", "info",
        "-f", "rawvideo",                                            # input format 'raw'
        "-framerate", "10.0",                                        # input framerate
        "-s", "100x200",                                             # input dimension
        "-pix_fmt", "rgba",                                          # input pixel format
        "-i", "-",                                                   # input file stdin
        "-r", "30",                                                  # output framerate
        "-vcodec", "libx264",                                        # output format
        "-preset", "veryfast",                                       # output quality/encoding preset
        "output"                                                     # output file
    ]
