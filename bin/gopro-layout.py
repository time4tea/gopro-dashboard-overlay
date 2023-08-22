#!/usr/bin/env python3

import argparse
import os
import pathlib
import random
from datetime import timedelta
from time import sleep
from xml.etree import ElementTree

from PIL import Image
from pint import DimensionalityError

from gopro_overlay import fake, geo, timeseries_process
from gopro_overlay.arguments import default_config_location
from gopro_overlay.assertion import assert_file_exists
from gopro_overlay.config import Config
from gopro_overlay.dimensions import dimension_from, Dimension
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro
from gopro_overlay.font import load_font
from gopro_overlay.framemeta import LoadFlag
from gopro_overlay.geo import MapRenderer, api_key_finder, MapStyler
from gopro_overlay.layout import Overlay
from gopro_overlay.layout_xml import layout_from_xml, load_xml_layout
from gopro_overlay.loading import GoproLoader
from gopro_overlay.log import log
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units
from gopro_overlay.widgets.widgets import SimpleFrameSupplier


def load_frame(ffmpeg_gopro: FFMPEGGoPro, filepath: pathlib.Path, size: Dimension, at_time=timeunits(seconds=2)):
    return Image.frombytes(mode="RGBA", size=size.tuple(), data=ffmpeg_gopro.load_frame(filepath, at_time))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Continually parse a layout file, and render a frame")
    parser.add_argument("--ffmpeg-dir", type=pathlib.Path,
                        help="Directory where ffmpeg/ffprobe located, default=Look in PATH")

    parser.add_argument("file", type=pathlib.Path, help="Input layout file")

    parser.add_argument("--map-style", choices=geo.map_styles, default="osm", help="Style of map to render")
    parser.add_argument("--map-api-key", help="API Key for map provider, if required (default OSM doesn't need one)")
    parser.add_argument("--config-dir", help="Location of config files (api keys, profiles, ...)", type=pathlib.Path,
                        default=default_config_location)
    parser.add_argument("--cache-dir", help="Location of caches (map tiles, ...)", type=pathlib.Path,
                        default=default_config_location)

    parser.add_argument("--font", help="Selects a font", default="Roboto-Medium.ttf")
    parser.add_argument("--overlay-size", default="1920x1080", help="Size of frame, XxY, e.g. 1920x1080")
    parser.add_argument("--gopro", type=pathlib.Path, help="Use gopro video to supply a background image / journey")

    args = parser.parse_args()

    config_dir = args.config_dir
    config_dir.mkdir(exist_ok=True)

    cache_dir = args.cache_dir
    cache_dir.mkdir(exist_ok=True)

    font = load_font(args.font)

    config_loader = Config(config_dir)
    key_finder = api_key_finder(config_loader, args)

    font = font.font_variant(size=16)

    layout_file: pathlib.Path = args.file

    rng = random.Random()
    rng.seed(12345)

    frame = None
    video_frame = None

    ffmpeg_gopro = FFMPEGGoPro(FFMPEG(args.ffmpeg_dir))

    if args.gopro:
        inputpath = assert_file_exists(args.gopro)

        loader = GoproLoader(
            ffmpeg_gopro=ffmpeg_gopro,
            units=units,
            flags={LoadFlag.ACCL, LoadFlag.CORI, LoadFlag.GRAV},
        )

        gopro = loader.load(inputpath)

        dimensions = gopro.recording.video.dimension
        timeseries = gopro.framemeta

        timeseries.process_deltas(timeseries_process.calculate_speeds(), skip=18 * 3)
        timeseries.process(timeseries_process.calculate_odo())
        timeseries.process_deltas(timeseries_process.calculate_gradient(), skip=18 * 3)

        video_frame = load_frame(ffmpeg_gopro, inputpath, gopro.recording.video.dimension, timeseries.mid)

    else:
        timeseries = fake.fake_framemeta(timedelta(minutes=5), step=timedelta(seconds=1), rng=rng, point_step=0.0001)

    with MapRenderer(
            cache_dir=cache_dir,
            styler=MapStyler(api_key_finder=key_finder)
    ).open(args.map_style) as renderer:

        last_updated = None

        while True:
            if not layout_file.exists():
                log(f"Layout file not found: {layout_file}")
                sleep(1)
            else:
                updated = os.stat(layout_file).st_mtime

                if updated != last_updated:
                    last_updated = updated

                    try:
                        layout = layout_from_xml(load_xml_layout(args.file), renderer, timeseries, font,
                                                 NoPrivacyZone())

                        overlay = Overlay(
                            framemeta=timeseries,
                            create_widgets=layout
                        )

                        supplier = SimpleFrameSupplier(dimension_from(args.overlay_size))
                        frame = overlay.draw(timeseries.mid, supplier.drawing_frame())

                        if video_frame is not None:
                            frame = Image.alpha_composite(video_frame, frame)

                        frame.save("frame.png")
                        log("Saved Image")

                    except IOError as e:
                        log(f"Unable to load {layout_file}: {e}")
                    except ElementTree.ParseError as e:
                        log(f"Unable to load {layout_file}: XML Parsing Error: {e}")
                    except DimensionalityError as e:
                        log(f"Unable to load {layout_file}: Unit Conversion: {e}")
                    except ValueError as e:
                        log(f"Unable to load {layout_file}: {e}")

            sleep(0.1)
