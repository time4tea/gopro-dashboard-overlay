#!/usr/bin/env python3

import argparse
import pathlib

from gopro_overlay.ffmpeg import find_recording

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract GoPro metadata to data file")

    parser.add_argument("input", type=pathlib.Path, help="Input file")
    parser.add_argument("output", type=pathlib.Path, nargs="?", default="-", help="Output file (default stdout)")

    args = parser.parse_args()

    dest: pathlib.Path = args.output
    source: pathlib.Path = args.input

    recording = find_recording(source)

    with dest.open("wb") as output:
        output.write(recording.load_gpmd())
