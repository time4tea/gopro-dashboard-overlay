#!/usr/bin/env python3

import argparse
import os.path
import pathlib
import re
from typing import List

from gopro_overlay import functional, filenaming, ffmpeg, geocode
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.gpmd_visitors_gps import DetermineFirstLockedGPSUVisitor
from gopro_overlay.log import log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename a series of GoPro files by date. Does nothing (so its safe) by default.")

    parser.add_argument("file", type=pathlib.Path, nargs="+", help="The files to rename, or directory/ies containing files")
    parser.add_argument("-t", "--touch", action="store_true", help="change the modification time of the file")
    parser.add_argument("-to", "--touch-only", action="store_true", help="change the modification time of the file only - don't rename")
    parser.add_argument("--desc", help="a descriptive name to add to the filename - the filename will be yyyymmdd-hhmmss-{desc}.MP4")
    parser.add_argument("--geo", action="store_true", help="[EXPERIMENTAL] Use Geocode.xyz to add description for you (city-state) - see https://geocode.xyz/pricing for terms")
    parser.add_argument("-y", "--yes", action="store_true", help="Rename the files, don't just print what would be done")
    parser.add_argument("--dirs", action="store_true", help="Allow directory")
    parser.add_argument("--geocode-key", help="geocode.xyz api key")

    args = parser.parse_args()

    if not args.yes:
        log("*** DRY RUN - NOT ACTUALLY DOING ANYTHING ***")

    inputs: List[pathlib.Path] = args.file

    for path in inputs:
        if not path.exists():
            raise IOError(f"File not found {path}")
        if path.is_dir() and not args.dirs:
            raise IOError(f"{path} is a directory, please use --dirs")

    potentials = functional.flatten([filenaming.gopro_files_in(path) for path in inputs])
    potentials = filter(None, potentials)
    file_list = sorted(potentials)

    should_touch = args.touch or args.touch_only
    should_rename = not args.touch_only

    geocoder = geocode.GeoCode(key=args.geocode_key)

    for file in file_list:
        meta = GoproMeta.parse(ffmpeg.load_gpmd_from(file))
        found = meta.accept(DetermineFirstLockedGPSUVisitor())
        gps_datetime = found.packet_time
        if gps_datetime is None:
            log(f"Unable to determine GPS date for {file} - GPS never locked")
            continue

        formatted_datetime = gps_datetime.strftime("%Y%m%d-%H%M%S")

        if args.desc:
            new_name = f"{formatted_datetime}-{args.desc}.MP4"
        elif args.geo:
            geojson = geocoder.geocode_location(found.point.lat, found.point.lon)
            city = geojson["city"].lower()
            if "state" in geojson:
                state = geojson["state"].lower()
            elif "region" in geojson:
                state = geojson["region"].lower()
            elif "prov" in geojson:
                state = geojson["prov"].lower()
            else:
                state = "unknown"

            desc = re.sub(r'[^\w_\-.]', '-', f"{city}-{state}")
            new_name = f"{formatted_datetime}-{desc}.MP4"
        else:
            new_name = f"{formatted_datetime}.MP4"

        new_file = file.with_name(new_name)

        if should_rename:
            log(f"Rename {file} to {new_file}")
        if should_touch:
            log(f"Update time to {gps_datetime}")

        if args.yes:
            if should_touch:
                epoch_seconds = int(gps_datetime.strftime("%s"))
                os.utime(file, times=(epoch_seconds, epoch_seconds))

            if should_rename:
                file.rename(new_file)
