#!/usr/bin/env python3

import argparse
import os
import pathlib
import random
import traceback
from datetime import timedelta
from subprocess import TimeoutExpired
from time import sleep
from xml.etree import ElementTree

from PIL import Image
from pint import DimensionalityError

from gopro_overlay import fake, geo, ffmpeg
from gopro_overlay.arguments import default_config_location
from gopro_overlay.dimensions import dimension_from, Dimension
from gopro_overlay.ffmpeg import find_streams
from gopro_overlay.font import load_font
from gopro_overlay.framemeta import framemeta_from
from gopro_overlay.geo import CachingRenderer, api_key_finder
from gopro_overlay.layout import Overlay
from gopro_overlay.layout_xml import layout_from_xml, load_xml_layout
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units


def load_frame(filepath: pathlib.Path, size: Dimension, at_time=timeunits(seconds=2)):
    return Image.frombytes(mode="RGBA", size=size.tuple(), data=ffmpeg.load_frame(filepath, at_time))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Continually parse a layout file, and render a frame")

    parser.add_argument("file", type=pathlib.Path, help="Input layout file")

    parser.add_argument("--map-style", choices=geo.map_styles, default="osm", help="Style of map to render")
    parser.add_argument("--map-api-key", help="API Key for map provider, if required (default OSM doesn't need one)")
    parser.add_argument("--config-dir", help="Location of config files (api keys, profiles, ...)", type=pathlib.Path,
                        default=default_config_location)
    parser.add_argument("--cache-dir", help="Location of caches (map tiles, ...)", type=pathlib.Path,
                        default=default_config_location)

    parser.add_argument("--font", help="Selects a font", default="Roboto-Medium.ttf")
    parser.add_argument("--overlay-size", default="1920x1080", help="Size of frame, XxY, e.g. 1920x1080")
    parser.add_argument("--gopro", type=pathlib.Path,  help="Use gopro video to supply a background image / journey")

    args = parser.parse_args()

    config_dir = args.config_dir
    config_dir.mkdir(exist_ok=True)

    cache_dir = args.cache_dir
    cache_dir.mkdir(exist_ok=True)

    font = load_font(args.font)

    key_finder = api_key_finder(args, config_dir=config_dir)

    font = font.font_variant(size=16)

    layout_file: pathlib.Path = args.file

    rng = random.Random()
    rng.seed(12345)

    frame = None
    video_frame = None

    if args.gopro:
        inputpath = args.gopro
        stream_info = find_streams(inputpath)

        if not stream_info.meta:
            raise IOError(f"Unable to locate metadata stream in '{inputpath}' - is it a GoPro file")

        dimensions = stream_info.video.dimension
        try:
            timeseries = framemeta_from(inputpath, metameta=stream_info.meta, units=units)

            mid_point = timeseries.min + ((timeseries.max - timeseries.min) / 2)

            video_frame = load_frame(inputpath, stream_info.video.dimension, mid_point)


        except TimeoutExpired:
            traceback.print_exc()
            print(f"{inputpath} appears to be located on a slow device. Please ensure both input and output files are on fast disks")
            exit(1)

    else:
        timeseries = fake.fake_framemeta(timedelta(minutes=5), step=timedelta(seconds=1), rng=rng, point_step=0.0001)

    with CachingRenderer(
            cache_dir=cache_dir,
            style=args.map_style,
            api_key_finder=key_finder).open() as renderer:

        last_updated = None

        while True:
            if not layout_file.exists():
                print(f"Layout file not found: {layout_file}")

            updated = os.stat(layout_file).st_mtime

            if updated != last_updated:
                last_updated = updated

                try:
                    layout = layout_from_xml(load_xml_layout(args.file), renderer, timeseries, font, NoPrivacyZone())

                    overlay = Overlay(
                        dimensions=dimension_from(args.overlay_size),
                        framemeta=timeseries,
                        create_widgets=layout
                    )

                    mid_point = timeseries.min + ((timeseries.max - timeseries.min) / 2)
                    frame = overlay.draw(mid_point)

                    if video_frame is not None:
                        frame = Image.alpha_composite(video_frame, frame)

                    frame.save("frame.png")

                except IOError as e:
                    print(f"Unable to load {layout_file}: {e}")
                except ElementTree.ParseError as e:
                    print(f"Unable to load {layout_file}: XML Parsing Error: {e}")
                except DimensionalityError as e:
                    print(f"Unable to load {layout_file}: Unit Conversion: {e}")

            sleep(0.1)
