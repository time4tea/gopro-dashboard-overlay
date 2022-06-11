#!/usr/bin/env python3

import argparse
import os.path
import re

from gopro_overlay import functional, filenaming, ffmpeg, geocode
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.gpmd_visitors_gps import DetermineFirstLockedGPSUVisitor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename a series of GoPro files by date. Does nothing (so its safe) by default.")

    parser.add_argument("file", nargs="+", help="The files to rename, or directory/ies containing files")
    parser.add_argument("--desc", help="a descriptive name to add to the filename - the filename will be yyyymmdd-hhmmss-{desc}.MP4")
    parser.add_argument("--geo", action="store_true", help="[EXPERIMENTAL] Use Geocode.xyz to add description for you (city-state) - see https://geocode.xyz/pricing for terms")
    parser.add_argument("--yes", action="store_true", help="Rename the files, don't just print what would be done")
    parser.add_argument("--dirs", action="store_true", help="Allow directory")

    args = parser.parse_args()

    if not args.yes:
        print("*** DRY RUN - NOT ACTUALLY DOING ANYTHING ***")

    for path in args.file:
        if not os.path.exists(path):
            raise IOError(f"File not found {path}")
        if os.path.isdir(path) and not args.dirs:
            raise IOError(f"{path} is a directory, please use --dirs")

    potentials = functional.flatten([filenaming.gopro_files_in(path) for path in args.file])
    potentials = filter(None, potentials)
    file_list = sorted(potentials)

    for file in file_list:
        meta = GoproMeta.parse(ffmpeg.load_gpmd_from(file))
        found = meta.accept(DetermineFirstLockedGPSUVisitor())
        gps_datetime = found.packet_time
        if gps_datetime is None:
            print(f"Unable to determine GPS date for {file} - GPS never locked")
            continue

        formatted_datetime = gps_datetime.strftime("%Y%m%d-%H%M%S")

        if args.desc:
            new_name = f"{formatted_datetime}-{args.desc}.MP4"
        elif args.geo:
            geojson = geocode.geocode_location(found.point.lat, found.point.lon)
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

        print(f"Rename {file} to {new_file}")

        if args.yes:
            file.rename(new_file)
