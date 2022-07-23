from typing import List, Union

from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGOptions


class FFMPEGExecute:
    pass


class FFMPEGFake:

    def __init__(self):
        self.commands = None

    @property
    def command_line(self):
        return self.commands


class FFMPEGOverlayMulti:

    def __init__(self, runner: Union[FFMPEGExecute, FFMPEGFake],
                 inputs: List[str],
                 output: str,
                 overlay_size: Dimension,
                 options: FFMPEGOptions = None):
        pass

    def generate(self):
        pass


def test_ffmpeg_multi():
    # def __init__(self, input, output, overlay_size: Dimension, options: FFMPEGOptions = None, vsize=1080, execution=None):

    runner = FFMPEGFake()
    ff = FFMPEGOverlayMulti(
        runner=runner,
        inputs=["fileA", "fileB", "fileC"],
        output="overlaid",
        overlay_size=Dimension(5, 10)
    )

    ff.generate()

    assert runner.command_line == [
        "-y",
        "-i", "fileA",
        "-i", "fileB",
        "-i", "fileC",
        "-f", "rawvideo",
        "-framerate", "10.0",
        "-s", "5x10",
        "-pix_fmt", "rgba",
        "-i", "-",
        "-filter_complex", "[0:v][0:a][1:v][1:a][2:v][2:a]concat:n=3:v=1:a=1[vv][a];[vv][3:v]overlay",
        "overlaid"
    ]
