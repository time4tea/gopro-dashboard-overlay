import argparse
import pathlib
import sys

from gopro_overlay import geo
from gopro_overlay.log import fatal
from gopro_overlay.point import Point, BoundingBox


class SplitArgs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.split(','))


class SplitArgsFloat(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, tuple(map(float, values.split(","))))


class BBoxArgs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        bbox = tuple(map(float, values.split(",")))
        if len(bbox) != 4:
            raise ValueError("Bounding Box requires 4 values - minlon,minlat,maxlon,maxlat")
        extent_min = Point(lon=bbox[0], lat=bbox[1])
        extent_max = Point(lon=bbox[2], lat=bbox[3])
        setattr(namespace, self.dest, BoundingBox(min=extent_min, max=extent_max))


default_config_location = pathlib.Path.home() / ".gopro-graphics"


def gopro_dashboard_arguments(args=None):
    parser = argparse.ArgumentParser(
        description="Overlay gadgets on to GoPro MP4",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("input", type=pathlib.Path, nargs="?", help="Input MP4 file - Optional with --use-gpx-only")
    parser.add_argument("output", type=pathlib.Path,
                        help="Output Video File - MP4/MOV/WEBM all supported, see Profiles documentation")

    parser.add_argument("--font", help="Selects a font", default="Roboto-Medium.ttf")
    parser.add_argument("--gpx", "--fit", type=pathlib.Path,
                        help="Use GPX/FIT file for location / alt / hr / cadence / temp ...")
    parser.add_argument("--privacy", help="Set privacy zone (lat,lon,km)")

    parser.add_argument("--generate", choices=["default", "overlay", "none"], default="default",
                        help="Type of output to generate")
    parser.add_argument("--overlay-size",
                        help="<XxY> e.g. 1920x1080 Force size of overlay. "
                             "Use if video differs from supported bundled overlay sizes (1920x1080, 3840x2160), Required if --use-gpx-only")
    parser.add_argument("--profile",
                        help="Use ffmpeg options profile <name> from ~/gopro-graphics/ffmpeg-profiles.json")

    parser.add_argument("--config-dir", help="Location of config files (api keys, profiles, ...)", type=pathlib.Path,
                        default=default_config_location)
    parser.add_argument("--cache-dir", help="Location of caches (map tiles, ...)", type=pathlib.Path,
                        default=default_config_location)

    parser.add_argument("--double-buffer", action="store_true", help="Enable HIGHLY EXPERIMENTAL double buffering mode. May speed things up. May not work at all")

    only = parser.add_argument_group("GPX Only", "Creating Movies from GPX File only")

    only.add_argument("--use-gpx-only", "--use-fit-only", action="store_true",
                      help="Use only the GPX/FIT file - no GoPro location data")
    only.add_argument("--video-time-start", choices=["file-created", "file-modified", "file-accessed"],
                      help="Use file dates for aligning video and GPS information, only when --use-gpx-only - EXPERIMENTAL! - may be changed/removed")
    only.add_argument("--video-time-end", choices=["file-created", "file-modified", "file-accessed"],
                      help="Use file dates for aligning video and GPS information, only when --use-gpx-only - EXPERIMENTAL! - may be changed/removed")

    maps = parser.add_argument_group("Mapping", "Display of Maps")

    maps.add_argument("--map-style", choices=geo.map_styles, default="osm", help="Style of map to render")
    maps.add_argument("--map-api-key", help="API Key for map provider, if required (default OSM doesn't need one)")

    layout = parser.add_argument_group("Layout", "Controlling layout")

    layout.add_argument("--layout", choices=["default", "speed-awareness", "xml"], default="default",
                        help="Choose graphics layout")

    layout.add_argument("--layout-xml", type=pathlib.Path, help="Use XML File for layout")

    layout.add_argument("--exclude", nargs="+", help="exclude named component (will include all others")
    layout.add_argument("--include", nargs="+", help="include named component (will exclude all others)")

    units = parser.add_argument_group("Units", "Controlling Units")

    units.add_argument("--units-speed", default="mph", help="Default unit for speed. Many units supported: mph, mps, kph, kph, knot, ...")
    units.add_argument("--units-altitude", default="metre", help="Default unit for altitude. Many units supported: foot, mile, metre, meter, parsec, angstrom, ...")
    units.add_argument("--units-distance", default="mile", help="Default unit for distance. Many units supported: mile, km, foot, nmi, meter, metre, parsec, ...")
    units.add_argument("--units-temperature", default="degC", choices=["kelvin", "degC", "degF"], help="Default unit for temperature")

    gps = parser.add_argument_group("GPS", "Controlling GPS Parsing (from GoPro Only)")

    gps.add_argument("--gps-dop-max", type=float, default=10, help="Max DOP - Points with greater DOP will be considered 'Not Locked'")
    gps.add_argument("--gps-speed-max", type=float, default=60, help="Max GPS Speed - Points with greater speed will be considered 'Not Locked'")
    gps.add_argument("--gps-speed-max-units", default="kph", help="Units for --gps-speed-max")
    gps.add_argument("--gps-bbox-lon-lat", action=BBoxArgs, help="Define GPS Bounding Box, anything outside will be considered 'Not Locked' - minlon,minlat,maxlon,maxlat")

    debugging = parser.add_argument_group("Debugging", "Controlling debugging outputs")

    debugging.add_argument("--show-ffmpeg", action="store_true", help="Show FFMPEG output (not usually useful)")
    debugging.add_argument("--debug-metadata", action="store_true", default=False,
                           help="Show detailed information when parsing GoPro Metadata")
    debugging.add_argument("--profiler", action="store_true",
                           help="Do some basic profiling of the widgets to find ones that may be slow")
    args = parser.parse_args(args)

    def quit(reason):
        parser.print_help(file=sys.stderr)
        fatal(f"Invalid arguments: {reason}")

    if (args.video_time_start or args.video_time_end) and not args.use_gpx_only:
        quit("--video-time-start/--video-time-end only applies when --use-gpx-only")

    if args.use_gpx_only and not args.gpx:
        quit("--gpx is required with --use-gpx-only")

    if args.use_gpx_only and not args.input and not args.overlay_size:
        quit("--overlay-size is required with --use-gpx-only (when no input video is given)")

    if args.use_gpx_only and args.generate != "default":
        quit("--generate cannot be combined with --use-gpx-only")

    return args
