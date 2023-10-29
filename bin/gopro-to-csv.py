#!/usr/bin/env python3

import argparse
import csv
import datetime
import pathlib
from pathlib import Path
from typing import Optional

from gopro_overlay import timeseries_process, gpmd_filters
from gopro_overlay.arguments import BBoxArgs
from gopro_overlay.assertion import assert_file_exists
from gopro_overlay.common import smart_open
from gopro_overlay.counter import ReasonCounter
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro
from gopro_overlay.framemeta import LoadFlag
from gopro_overlay.gpmf import GPSFix, GPS_FIXED_VALUES
from gopro_overlay.gpx import load_timeseries
from gopro_overlay.loading import GoproLoader
from gopro_overlay.units import units

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert GoPro MP4 file / GPX File to CSV")
    parser.add_argument("--ffmpeg-dir", type=pathlib.Path,
                        help="Directory where ffmpeg/ffprobe located, default=Look in PATH")

    parser.add_argument("--every", default=0, type=int,
                        help="Output a point every 'n' seconds. Default is output all points (usually 20/s)")
    parser.add_argument("--only-locked", action="store_true", help="Only output points where GPS is locked")

    parser.add_argument("--gps-dop-max", type=float, default=10,
                        help="Max DOP - Points with greater DOP will be considered 'Not Locked'")
    parser.add_argument("--gps-speed-max", type=float, default=60,
                        help="Max GPS Speed - Points with greater speed will be considered 'Not Locked'")
    parser.add_argument("--gps-speed-max-units", default="kph", help="Units for --gps-speed-max")
    parser.add_argument("--gps-bbox-lon-lat", action=BBoxArgs,
                        help="Define GPS Bounding Box, anything outside will be considered 'Not Locked' - minlon,minlat,maxlon,maxlat")

    parser.add_argument("input", type=pathlib.Path, help="Input file")
    parser.add_argument("output", type=pathlib.Path, nargs="?", default="-", help="Output CSV file (default stdout)")

    parser.add_argument("--gpx", action="store_true", help="Input is a gpx file")

    args = parser.parse_args()

    source = assert_file_exists(args.input)

    ffmpeg_gopro = FFMPEGGoPro(FFMPEG(args.ffmpeg_dir))

    if args.gpx:
        ts = load_timeseries(source, units)
    else:
        counter = ReasonCounter()

        loader = GoproLoader(
            ffmpeg_gopro=ffmpeg_gopro,
            units=units,
            flags={LoadFlag.ACCL, LoadFlag.CORI, LoadFlag.GRAV},
            gps_lock_filter=gpmd_filters.standard(
                dop_max=args.gps_dop_max,
                speed_max=units.Quantity(args.gps_speed_max, args.gps_speed_max_units),
                bbox=args.gps_bbox_lon_lat,
                report=counter.because
            )
        )

        gopro = loader.load(source)

        gpmd_filters.poor_report(counter)

        ts = gopro.framemeta

    packets_per_second = 18
    locked_2d = lambda e: e.gpsfix in GPS_FIXED_VALUES
    locked_3d = lambda e: e.gpsfix == GPSFix.LOCK_3D.value

    # ts.process(timeseries_process.process_ses("point", lambda i: i.point, alpha=0.45), filter_fn=locked_2d)
    ts.process_deltas(timeseries_process.calculate_speeds(), skip=packets_per_second * 3, filter_fn=locked_2d)
    ts.process(timeseries_process.calculate_odo(), filter_fn=locked_2d)
    ts.process_deltas(timeseries_process.calculate_gradient(), skip=packets_per_second * 3, filter_fn=locked_3d)  # hack
    ts.process(timeseries_process.filter_locked())

    filter_fn = locked_2d if args.only_locked else lambda e: True


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
                                            "grad",
                                            "accl_x", "accl_y", "accl_z"])
        writer.writeheader()
        for entry in filter(filter_fn, ts.items(step=datetime.timedelta(seconds=args.every))):
            writer.writerow({
                "packet": printable_unit(entry.packet),
                "packet_index": printable_unit(entry.packet_index),
                "gps_fix": GPSFix(entry.gpsfix).name,
                "date": entry.dt,
                "dop": printable_unit(entry.dop),
                "lat": entry.point.lat,
                "lon": entry.point.lon,
                "alt": printable_unit(entry.alt),
                "grad": printable_unit(entry.grad if entry.grad is not None else entry.cgrad),
                "speed": printable_unit(entry.speed if entry.speed is not None else entry.cspeed),
                "dist": printable_unit(entry.dist),
                "time": printable_unit(entry.time),
                "azi": printable_unit(entry.azi),
                "odo": printable_unit(entry.odo),
                "accl_x": printable_unit(entry.accl.x) if entry.accl else None,
                "accl_y": printable_unit(entry.accl.y) if entry.accl else None,
                "accl_z": printable_unit(entry.accl.z) if entry.accl else None
            })
