#!/usr/bin/env python3

import argparse
import pathlib

from gopro_overlay.ffmpeg import load_gpmd_from

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract GoPro metadata to data file")

    parser.add_argument("input", type=pathlib.Path, help="Input file")
    parser.add_argument("output", type=pathlib.Path, nargs="?", default="-", help="Output file (default stdout)")

    args = parser.parse_args()

    dest: pathlib.Path = args.output
    source: pathlib.Path = args.input

    with dest.open("wb") as output:
        output.write(load_gpmd_from(source))
