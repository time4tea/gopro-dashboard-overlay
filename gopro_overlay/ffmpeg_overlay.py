from __future__ import annotations

import contextlib
from pathlib import Path

from gopro_overlay.dimensions import Dimension
from gopro_overlay.execution import InProcessExecution
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.functional import flatten


class FFMPEGOptions:

    def __init__(self, input=None, output=None, filter_spec=None):
        self.input = input if input is not None else []
        self.output = output if output is not None else ["-vcodec", "libx264", "-preset", "veryfast"]
        self.filter_complex = filter_spec if filter_spec is not None else "[0:v][1:v]overlay"
        self.general = ["-hide_banner", "-loglevel", "info"]

    def set_input_options(self, options):
        self.input = options

    def set_output_options(self, options):
        self.output = options


class FFMPEGNull:

    def __init__(self):
        self.execution = InProcessExecution(redirect="/dev/null")

    @contextlib.contextmanager
    def generate(self):
        yield from self.execution.execute(["cat"])


class FFMPEGOverlay:

    def __init__(self, ffmpeg: FFMPEG, output: Path, overlay_size: Dimension, options: FFMPEGOptions = None,
                 execution=None):
        self.exe = ffmpeg
        self.output = output
        self.overlay_size = overlay_size
        self.execution = execution if execution else InProcessExecution()
        self.options = options if options else FFMPEGOptions()

    @contextlib.contextmanager
    def generate(self):
        cmd = flatten([
            "-hide_banner",
            "-y",
            self.options.general,
            "-f", "rawvideo",
            "-framerate", "10.0",
            "-s", f"{self.overlay_size.x}x{self.overlay_size.y}",
            "-pix_fmt", "rgba",
            "-i", "-",
            "-r", "30",
            self.options.output,
            str(self.output)
        ])

        yield from self.exe.execute(self.execution, cmd)


class FFMPEGOverlayVideo:

    def __init__(self, ffmpeg: FFMPEG, input: Path, output: Path, overlay_size: Dimension,
                 options: FFMPEGOptions = None,
                 execution=None):
        self.exe = ffmpeg
        self.output = output
        self.input = input
        self.options = options if options else FFMPEGOptions()
        self.overlay_size = overlay_size
        self.execution = execution if execution else InProcessExecution()

    @contextlib.contextmanager
    def generate(self):
        cmd = flatten([
            "-y",
            self.options.general,
            self.options.input,
            "-i", str(self.input),
            "-f", "rawvideo",
            "-framerate", "10.0",
            "-s", f"{self.overlay_size.x}x{self.overlay_size.y}",
            "-pix_fmt", "rgba",
            "-i", "-",
            "-filter_complex", self.options.filter_complex,
            self.options.output,
            str(self.output)
        ])

        yield from self.exe.execute(
            self.execution,
            cmd
        )
