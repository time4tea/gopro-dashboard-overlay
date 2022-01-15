import argparse

from gopro_overlay.gpx import load_timeseries
from gopro_overlay.journey import Journey
from gopro_overlay.units import units

# ## -0.29363,51.39235,-0.26822,51.39963

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Various random utilities for GPX files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--action", choices=["extents"], default="extents")

    parser.add_argument("gpx", help="GPX file")

    args = parser.parse_args()

    timeseries = load_timeseries(args.gpx, units)

    if args.action == "extents":
        journey = Journey()
        timeseries.process(journey.accept)
        bbox = journey.bounding_box

        print(f"{bbox[0].lon},{bbox[0].lat},{bbox[1].lon},{bbox[1].lat}")
        print(bbox)
