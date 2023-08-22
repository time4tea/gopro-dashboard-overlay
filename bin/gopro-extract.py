#!/usr/bin/env python3

import argparse
import pathlib

from gopro_overlay.assertion import assert_file_exists
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract GoPro metadata to data file")
    parser.add_argument("--ffmpeg-dir", type=pathlib.Path,
                        help="Directory where ffmpeg/ffprobe located, default=Look in PATH")

    parser.add_argument("input", type=pathlib.Path, help="Input file")
    parser.add_argument("output", type=pathlib.Path, nargs="?", default="-", help="Output file (default stdout)")

    args = parser.parse_args()

    dest: pathlib.Path = args.output
    source: pathlib.Path = assert_file_exists(args.input)

    ffmpeg_gopro = FFMPEGGoPro(FFMPEG(args.ffmpeg_dir))

    recording = ffmpeg_gopro.find_recording(source)

    with dest.open("wb") as output:
        output.write(recording.load_gpmd())
