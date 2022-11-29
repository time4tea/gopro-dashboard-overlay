#!/usr/bin/env python3

import argparse
import csv
import pathlib
import sys
from pathlib import Path
from typing import Optional

from gopro_overlay import timeseries_process
from gopro_overlay.common import smart_open
from gopro_overlay.ffmpeg import find_streams
from gopro_overlay.framemeta import framemeta_from
from gopro_overlay.gpmd import GPSFix
from gopro_overlay.gpx import load_timeseries
from gopro_overlay.units import units

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert GoPro MP4 file / GPX File to CSV")

    parser.add_argument("input", type=pathlib.Path, help="Input file")
    parser.add_argument("output", type=pathlib.Path, nargs="?", default="-", help="Output CSV file (default stdout)")

    parser.add_argument("--gpx", action="store_true", help="Input is a gpx file")

    args = parser.parse_args()

    source = args.input

    if not source.exists():
        print(f"{source}: No such file or directory", file=sys.stderr)
        exit(1)

    if args.gpx:
        ts = load_timeseries(source, units)
    else:
        stream_info = find_streams(source)
        ts = framemeta_from(source,
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


    dest: Optional[Path] = args.output

    with smart_open(dest) as f:
        writer = csv.DictWriter(f=f,
                                fieldnames=["packet", "packet_index", "gps_fix", "date", "lat", "lon", "dop", "alt",
                                            "speed",
                                            "dist", "time", "azi", "odo",
                                            "grad", "accl_x", "accl_y", "accl_z"])
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
                "accl_x": printable_unit(entry.accl.x) if entry.accl else None,
                "accl_y": printable_unit(entry.accl.y) if entry.accl else None,
                "accl_z": printable_unit(entry.accl.z) if entry.accl else None
            })
