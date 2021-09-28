#!/usr/bin/env python3

import argparse
import contextlib
import sys
from collections import Counter

import gpxpy

from gopro_overlay.ffmpeg import load_gpmd_from
from gopro_overlay.gpmd import GPMDParser, GPS5Scaler, GPMDInterpreter
from gopro_overlay.units import units


@contextlib.contextmanager
def smart_open(filename=None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert GoPro MP4 file to GPX")

    parser.add_argument("input", help="Input MP4 file")
    parser.add_argument("output", nargs="?", default="-", help="Output GPX file (default stdout)")

    args = parser.parse_args()

    parser = GPMDParser.parser(load_gpmd_from(args.input))

    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    counter = Counter()


    def add_point(entry):
        counter.update(["OK"])
        gpx_segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                time=entry.dt,
                latitude=entry.lat,
                longitude=entry.lon,
                elevation=entry.alt.to("m").magnitude)
        )


    scaler = GPS5Scaler(
        units,
        max_dop=6.0,
        on_item=lambda entry: add_point(entry),
        on_drop=lambda x: counter.update([x])
    )
    interpreter = GPMDInterpreter()

    for interpreted in interpreter.interpret(parser.items()):
        if interpreted.understood:
            scaler.accept(interpreted)

    with smart_open(args.output) as f:
        f.write(gpx.to_xml())

    print(counter)
