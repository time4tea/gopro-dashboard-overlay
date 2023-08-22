#!/usr/bin/env python3

import argparse
import datetime
import pathlib
from pathlib import Path
from typing import Optional

from gopro_overlay import gpmd_filters
from gopro_overlay.arguments import BBoxArgs
from gopro_overlay.assertion import assert_file_exists
from gopro_overlay.common import smart_open
from gopro_overlay.counter import ReasonCounter
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro
from gopro_overlay.framemeta_gpx import framemeta_to_gpx
from gopro_overlay.gpmd import GPS_FIXED_VALUES
from gopro_overlay.loading import GoproLoader
from gopro_overlay.log import log
from gopro_overlay.units import units

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert GoPro MP4 file to GPX")
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

    parser.add_argument("input", type=pathlib.Path, help="Input MP4 file")
    parser.add_argument("output", type=pathlib.Path, nargs="?", default="-", help="Output GPX file (default stdout)")

    args = parser.parse_args()

    source = assert_file_exists(args.input)

    log(f"Loading GoPro {source}")

    counter = ReasonCounter()

    ffmpeg_gopro = FFMPEGGoPro(FFMPEG(args.ffmpeg_dir))

    loader = GoproLoader(
        ffmpeg_gopro=ffmpeg_gopro,
        units=units,
        gps_lock_filter=gpmd_filters.standard(
            dop_max=args.gps_dop_max,
            speed_max=units.Quantity(args.gps_speed_max, args.gps_speed_max_units),
            bbox=args.gps_bbox_lon_lat,
            report=counter.because
        )
    )

    gopro = loader.load(source)

    gpmd_filters.poor_report(counter)

    fm = gopro.framemeta

    log("Generating GPX")

    locked_2d = lambda e: e.gpsfix in GPS_FIXED_VALUES
    filter_fn = locked_2d if args.only_locked else lambda e: True

    gpx = framemeta_to_gpx(fm, step=datetime.timedelta(seconds=args.every), filter_fn=filter_fn)

    dest: Optional[Path] = args.output

    with smart_open(dest) as f:
        f.write(gpx.to_xml())
