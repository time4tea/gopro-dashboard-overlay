#!/usr/bin/env python3

import argparse
import sys
from collections import Counter
from pathlib import Path

from gopro_overlay.common import smart_open
from gopro_overlay.gpmd import timeseries_from
from gopro_overlay.timeseries_gpx import timeseries_to_gpx
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

    ts = timeseries_from(args.input, units, on_drop=lambda reason: counter.update([reason]))

    gpx = timeseries_to_gpx(ts)

    with smart_open(args.output) as f:
        f.write(gpx.to_xml())

    print(counter, file=sys.stdout)
