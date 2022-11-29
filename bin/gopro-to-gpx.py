#!/usr/bin/env python3

import argparse
import datetime
import pathlib
import sys
from pathlib import Path
from typing import Optional

from gopro_overlay import ffmpeg
from gopro_overlay.common import smart_open
from gopro_overlay.framemeta import framemeta_from
from gopro_overlay.framemeta_gpx import framemeta_to_gpx
from gopro_overlay.units import units

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert GoPro MP4 file to GPX")

    parser.add_argument("--every", default=0, type=int, help="Output a point every 'n' seconds. Default is output all points (usually 20/s)")
    parser.add_argument("input", type=pathlib.Path, help="Input MP4 file")
    parser.add_argument("output", type=pathlib.Path, nargs="?", default="-", help="Output GPX file (default stdout)")

    args = parser.parse_args()

    source = args.input

    if not source.exists():
        print(f"{source}: No such file or directory", file=sys.stderr)
        exit(1)

    print(f"Loading GoPro {source}")

    stream_info = ffmpeg.find_streams(source)
    fm = framemeta_from(
        source,
        units=units,
        metameta=stream_info.meta
    )

    print("Generating GPX")

    gpx = framemeta_to_gpx(fm, step=datetime.timedelta(seconds=args.every))

    dest: Optional[Path] = args.output

    with smart_open(dest) as f:
        f.write(gpx.to_xml())
