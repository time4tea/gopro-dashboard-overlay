import argparse

from gopro_overlay import geo


def gopro_dashboard_arguments(args=None):
    parser = argparse.ArgumentParser(
        description="Overlay gadgets on to GoPro MP4",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("input", help="Input MP4 file")
    parser.add_argument("output", help="Output MP4 file")

    parser.add_argument("--font", help="Selects a font", default="Roboto-Medium.ttf")

    parser.add_argument("--gpx", help="Use GPX file for location / alt / hr / cadence / temp")
    parser.add_argument("--privacy", help="Set privacy zone (lat,lon,km)")

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

    parser.add_argument("--generate", choices=["default", "overlay", "none"], default="default", help="Type of output to generate")
    parser.add_argument("--show-ffmpeg", action="store_true", help="Show FFMPEG output (not usually useful)")

    parser.add_argument("--debug-metadata", action="store_true", default=False,
                        help="Show detailed information when parsing GoPro Metadata")

    parser.add_argument("--overlay-size",
                        help="<XxY> e.g. 1920x1080 Force size of overlay. "
                             "Use if video differs from supported bundled overlay sizes (1920x1080, 3840x2160)")

    parser.add_argument("--output-size", default="1080", type=int, help="Vertical size of output movie")

    parser.add_argument("--profile", help="(EXPERIMENTAL) Use ffmpeg options profile <name> from ~/gopro-graphics/ffmpeg-profiles.json")

    parser.add_argument("--thread", action="store_true", help="(VERY EXPERIMENTAL MAY CRASH) Use an intermediate buffer before ffmpeg as possible performance enhancement")
    return parser.parse_args(args)
