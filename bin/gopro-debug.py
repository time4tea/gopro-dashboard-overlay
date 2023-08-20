#!/usr/bin/env python3

import argparse
import pathlib

from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.gpmd_visitors_debug import DebuggingVisitor
from gopro_overlay.log import log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Output some debugging information about a GoPro file")
    parser.add_argument("--ffmpeg-dir", type=pathlib.Path, help="Directory where ffmpeg/ffprobe located, default=Look in PATH")

    parser.add_argument("input", type=pathlib.Path, help="Input file")

    args = parser.parse_args()

    source: pathlib.Path = args.input

    if not source.exists():
        log(f"{source}: File not  found")
        exit(1)

    ffmpeg_gopro = FFMPEGGoPro(FFMPEG(args.ffmpeg_dir))

    recording = ffmpeg_gopro.find_recording(source)

    log(f"Stream Info: {recording}")

    GoproMeta.parse(recording.load_gpmd()).accept(DebuggingVisitor())
