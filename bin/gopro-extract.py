#!/usr/bin/env python3

import argparse

from gopro_overlay.ffmpeg import load_gpmd_from

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract GoPro metadata to data file")

    parser.add_argument("input", help="Input file")
    parser.add_argument("output", nargs="?", default="-", help="Output file (default stdout)")

    args = parser.parse_args()

    with open(args.output, "wb") as output:
        output.write(load_gpmd_from(args.input))

