#!/usr/bin/env python3

import argparse
import csv
import sys
from pathlib import Path

from gopro_overlay import timeseries_process
from gopro_overlay.common import smart_open
from gopro_overlay.ffmpeg import find_streams
from gopro_overlay.framemeta import framemeta_from
from gopro_overlay.gpmd import GPSFix
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
        stream_info = find_streams(args.input)
        ts = framemeta_from(args.input,
                            units=units,
                            metameta=stream_info.meta
                            )

    ts.process_deltas(timeseries_process.calculate_speeds())
    ts.process(timeseries_process.calculate_odo())
    ts.process_deltas(timeseries_process.calculate_gradient(), skip=18 * 3)  # gradient hack


    def printable_unit(v):
        if v is None:
            return ""
        return v.magnitude


    with smart_open(args.output) as f:
        writer = csv.DictWriter(f=f,
                                fieldnames=["packet", "packet_index", "gps_fix", "date", "lat", "lon", "dop", "alt",
                                            "speed",
                                            "dist", "time", "azi", "odo",
                                            "grad"])
        writer.writeheader()
        for entry in ts.items():
            writer.writerow({
                "packet": printable_unit(entry.packet),
                "packet_index": printable_unit(entry.packet_index),
                "gps_fix": GPSFix(entry.gpsfix).name,
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
