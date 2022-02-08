#!/usr/bin/env python3

import argparse
import csv
import sys
from pathlib import Path

from gopro_overlay import timeseries_process
from gopro_overlay.common import smart_open
from gopro_overlay.gpmd import timeseries_from
from gopro_overlay.gpx import load_timeseries
from gopro_overlay.units import units

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert GoPro MP4 file / GPX File to CSV")

    parser.add_argument("input", help="Input file")
    parser.add_argument("output", nargs="?", default="-", help="Output CSV file (default stdout)")

    parser.add_argument("--gpx", action="store_true", help="Input is a gpx file")

    args = parser.parse_args()

    input = args.input

    if not Path(input).exists():
        print(f"{input}: No such file or directory", file=sys.stderr)
        exit(1)

    if args.gpx:
        ts = load_timeseries(args.input, units)
    else:
        ts = timeseries_from(args.input,
                             units=units,
                             on_drop=lambda reason: print(reason),
                             )

    ts.process_deltas(timeseries_process.calculate_speeds())
    ts.process(timeseries_process.calculate_odo())
    ts.process_deltas(timeseries_process.calculate_gradient(), skip=10)


    def printable_unit(v):
        if v is None:
            return ""
        return v.magnitude


    with smart_open(args.output) as f:
        writer = csv.DictWriter(f=f,
                                fieldnames=["packet", "packet_index", "date", "lat", "lon", "dop", "alt", "speed",
                                            "dist", "time", "azi", "odo",
                                            "grad"])
        writer.writeheader()
        for entry in ts.items():
            writer.writerow({
                "packet": printable_unit(entry.packet),
                "packet_index": printable_unit(entry.packet_index),
                "date": entry.dt,
                "dop": printable_unit(entry.dop),
                "lat": entry.point.lat,
                "lon": entry.point.lon,
                "alt": printable_unit(entry.alt),
                "grad": printable_unit(entry.grad),
                "speed": printable_unit(entry.speed),
                "dist": printable_unit(entry.dist),
                "time": printable_unit(entry.time),
                "azi": printable_unit(entry.azi),
                "odo": printable_unit(entry.odo),
            })
