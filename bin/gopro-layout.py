#!/usr/bin/env python3

import argparse
import os
import pathlib
import random
from datetime import timedelta
from time import sleep
from xml.etree import ElementTree

from pint import DimensionalityError

from gopro_overlay import fake, geo
from gopro_overlay.dimensions import dimension_from
from gopro_overlay.font import load_font
from gopro_overlay.geo import CachingRenderer, api_key_finder
from gopro_overlay.layout import Overlay
from gopro_overlay.layout_xml import layout_from_xml, load_xml_layout
from gopro_overlay.privacy import NoPrivacyZone

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Continually parse a layout file, and render a frame")

    parser.add_argument("file", type=pathlib.Path, help="Input layout file")

    parser.add_argument("--map-style", choices=geo.map_styles, default="osm", help="Style of map to render")
    parser.add_argument("--map-api-key", help="API Key for map provider, if required (default OSM doesn't need one)")

    parser.add_argument("--font", help="Selects a font", default="Roboto-Medium.ttf")
    parser.add_argument("--overlay-size", default="1920x1080", help="Size of frame, XxY, e.g. 1920x1080")

    args = parser.parse_args()
    font = load_font(args.font)

    key_finder = api_key_finder(args)

    font = font.font_variant(size=16)

    layout_file: pathlib.Path = args.file

    rng = random.Random()
    rng.seed(12345)

    timeseries = fake.fake_framemeta(timedelta(minutes=5), step=timedelta(seconds=1), rng=rng, point_step=0.0001)

    with CachingRenderer(style=args.map_style, api_key_finder=key_finder).open() as renderer:

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

                    frame = overlay.draw(timeseries.min + ((timeseries.max - timeseries.min) / 2))
                    frame.save("frame.png")

                except IOError as e:
                    print(f"Unable to load {layout_file}: {e}")
                except ElementTree.ParseError as e:
                    print(f"Unable to load {layout_file}: XML Parsing Error: {e}")
                except DimensionalityError as e:
                    print(f"Unable to load {layout_file}: Unit Conversion: {e}")

            sleep(1)
