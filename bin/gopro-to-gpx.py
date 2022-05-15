#!/usr/bin/env python3

import argparse
import sys
from collections import Counter
from pathlib import Path

from gopro_overlay import ffmpeg
from gopro_overlay.common import smart_open
from gopro_overlay.framemeta import framemeta_from
from gopro_overlay.framemeta_gpx import framemeta_to_gpx
from gopro_overlay.units import units

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert GoPro MP4 file to GPX")

    parser.add_argument("input", help="Input MP4 file")
    parser.add_argument("output", nargs="?", default="-", help="Output GPX file (default stdout)")

    args = parser.parse_args()

    input = args.input

    if not Path(input).exists():
        print(f"{input}: No such file or directory", file=sys.stderr)
        exit(1)

    counter = Counter()

    stream_info = ffmpeg.find_streams(args.input)
    fm = framemeta_from(
        args.input,
        units=units,
        metameta=stream_info.meta
    )

    gpx = framemeta_to_gpx(fm)

    with smart_open(args.output) as f:
        f.write(gpx.to_xml())

    print(counter, file=sys.stdout)
