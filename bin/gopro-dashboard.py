#!/usr/bin/env python3

import argparse
import datetime
import os
import tempfile
from datetime import timedelta
from pathlib import Path

import progressbar

from gopro_overlay import timeseries_process, geo
from gopro_overlay.ffmpeg import FFMPEGOverlay, FFMPEGGenerate, ffmpeg_is_installed, ffmpeg_libx264_is_installed
from gopro_overlay.font import load_font
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.gpmd import timeseries_from
from gopro_overlay.gpx import load_timeseries
from gopro_overlay.layout import Overlay, speed_awareness_layout
from gopro_overlay.layout_xml import layout_from_xml, load_xml_layout
from gopro_overlay.point import Point
from gopro_overlay.privacy import PrivacyZone, NoPrivacyZone
from gopro_overlay.timing import PoorTimer
from gopro_overlay.units import units


def temp_file_name():
    handle, path = tempfile.mkstemp()
    os.close(handle)
    return path


def accepter_from_args(include, exclude):
    if include and exclude:
        raise ValueError("Can't use both include and exclude at the same time")

    if include:
        return lambda n: n in include
    if exclude:
        return lambda n: n not in exclude

    return lambda n: True


def create_desired_layout(layout_name, include, exclude, renderer, timeseries, font, privacy_zone):

    accepter = accepter_from_args(include, exclude)

    if layout_name == "default":
        return layout_from_xml(load_xml_layout("default-1080"), renderer, timeseries, font, privacy_zone, include=accepter)
    elif layout_name == "speed-awareness":
        return speed_awareness_layout(renderer, font=font)
    elif args.layout == "xml":

        return layout_from_xml(load_xml_layout(layout_name), renderer, timeseries, font, privacy_zone, include=accepter)
    else:
        raise ValueError(f"Unsupported layout {args.layout}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Overlay gadgets on to GoPro MP4",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("input", help="Input MP4 file")

    parser.add_argument("--font", help="Selects a font", default="Roboto-Medium.ttf")

    parser.add_argument("--gpx", help="Use GPX file for location / alt / hr / cadence / temp")
    parser.add_argument("--privacy", help="Set privacy zone (lat,lon,km)")

    parser.add_argument("--no-overlay", action="store_false", help="Only output the gadgets, don't overlay")
    parser.set_defaults(overlay=True)

    parser.add_argument("--map-style", choices=geo.map_styles, default="osm", help="Style of map to render")
    parser.add_argument("--map-api-key", help="API Key for map provider, if required (default OSM doesn't need one)")

    parser.add_argument("--layout", choices=["default", "speed-awareness", "xml"], default="default",
                        help="Choose graphics layout")

    parser.add_argument("--layout-xml",
                        help="Use XML File for layout [experimental! - file format likely to change!]")

    parser.add_argument("--exclude", nargs="+",
                        help="exclude named component (will include all others")
    parser.add_argument("--include", nargs="+",
                        help="include named component (will exclude all others)")

    parser.add_argument("--show-ffmpeg", action="store_true", help="Show FFMPEG output (not usually useful)")
    parser.set_defaults(show_ffmpeg=False)

    parser.add_argument("--output-size", default="1080", type=int, help="Vertical size of output movie")

    parser.add_argument("output", help="Output MP4 file")

    args = parser.parse_args()

    if not ffmpeg_is_installed():
        print("Can't start ffmpeg - is it installed?")
        exit(1)
    if not ffmpeg_libx264_is_installed():
        print("ffmpeg doesn't seem to handle libx264 files - it needs to be compiled with support for this, "
              "check your installation")
        exit(1)

    font = load_font(args.font)

    with PoorTimer("program").timing():

        gopro_timeseries = timeseries_from(args.input, units)
        print(f"GoPro Timeseries has {len(gopro_timeseries)} data points")

        if args.gpx:
            gpx_timeseries = load_timeseries(args.gpx, units)
            print(f"GPX Timeseries has {len(gpx_timeseries)} data points")
            timeseries = gpx_timeseries.clip_to(gopro_timeseries)
            print(f"GPX Timeseries overlap with GoPro - {len(timeseries)}")
            if not len(timeseries):
                raise ValueError("No overlap between GoPro and GPX file")
        else:
            timeseries = gopro_timeseries

        # bodge- fill in missing points to make smoothing easier to write.
        backfilled = timeseries.backfill(datetime.timedelta(seconds=1))
        if backfilled:
            print(f"Created {backfilled} missing points...")

        # smooth GPS points
        print("Processing....")
        timeseries.process(timeseries_process.process_ses("point", lambda i: i.point, alpha=0.45))
        timeseries.process_deltas(timeseries_process.calculate_speeds())
        timeseries.process(timeseries_process.calculate_odo())
        timeseries.process_deltas(timeseries_process.calculate_gradient(), skip=10)
        # smooth azimuth (heading) points to stop wild swings of compass
        timeseries.process(timeseries_process.process_ses("azi", lambda i: i.azi, alpha=0.2))

        ourdir = Path.home().joinpath(".gopro-graphics")
        ourdir.mkdir(exist_ok=True)

        # privacy zone applies everywhere, not just at start, so might not always be suitable...
        if args.privacy:
            lat, lon, km = args.privacy.split(",")
            privacy_zone = PrivacyZone(
                Point(float(lat), float(lon)),
                units.Quantity(float(km), units.km)
            )
        else:
            privacy_zone = NoPrivacyZone()

        with CachingRenderer(style=args.map_style, api_key=args.map_api_key).open() as renderer:

            overlay = Overlay(timeseries,
                              create_desired_layout(
                                  args.layout,
                                  args.include, args.exclude,
                                  renderer, timeseries, font, privacy_zone)
                              )

            if args.overlay:
                redirect = None
                if not args.show_ffmpeg:
                    redirect = temp_file_name()
                    print(f"FFMPEG Output is in {redirect}")

                ffmpeg = FFMPEGOverlay(input=args.input, output=args.output, vsize=args.output_size, redirect=redirect)
            else:
                ffmpeg = FFMPEGGenerate(output=args.output)

            write_timer = PoorTimer("writing to ffmpeg")
            byte_timer = PoorTimer("image to bytes")
            draw_timer = PoorTimer("drawing frames")

            # Draw an overlay frame every 0.1 seconds
            stepper = timeseries.stepper(timedelta(seconds=0.1))
            progress = progressbar.ProgressBar(
                widgets=[
                    'Render: ',
                    progressbar.Counter(),
                    ' [', progressbar.Percentage(), '] ',
                    progressbar.Bar(), ' ', progressbar.ETA()
                ],
                poll_interval=2.0,
                max_value=len(stepper)
            )

            try:
                with ffmpeg.generate() as writer:
                    for index, dt in enumerate(stepper.steps()):
                        progress.update(index)
                        frame = draw_timer.time(lambda: overlay.draw(dt))
                        tobytes = byte_timer.time(lambda: frame.tobytes())
                        write_timer.time(lambda: writer.write(tobytes))
                    progress.finish()
            finally:
                for t in [byte_timer, write_timer, draw_timer]:
                    print(t)
