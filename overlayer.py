import argparse
import dbm
from datetime import datetime, timedelta
from pathlib import Path

from geographiclib.geodesic import Geodesic
from numpy import asarray

import timeseries
from geo import dbm_caching_renderer
from gpmd import timeseries_from
from image import Overlay
from units import units


class TimeSeriesDataSource:

    def __init__(self, timeseries):
        self._timeseries = timeseries
        self._dt = timeseries.min
        self._entry = self._timeseries.get(self._dt)

    def timerange(self, step: timedelta):
        end = self._timeseries.max
        running = self._timeseries.min
        while running <= end:
            yield running
            running += step

    def time_is(self, dt: datetime):
        self._dt = dt
        self._entry = self._timeseries.get(self._dt)

    def datetime(self):
        return self._dt

    def lat(self):
        return self._entry.lat

    def lon(self):
        return self._entry.lon

    def speed(self):
        return self._entry.speed

    def azimuth(self):
        return self._entry.azi

    def cadence(self):
        return self._entry.cad

    def heart_rate(self):
        return self._entry.hr

    def altitude(self):
        return self._entry.alt


def calculate_speeds(a, b):
    inverse = Geodesic.WGS84.Inverse(a.lat, a.lon, b.lat, b.lon)
    dist = units.Quantity(inverse['s12'], units.m)
    time = units.Quantity((b.dt - a.dt).total_seconds(), units.seconds)
    azi = units.Quantity(inverse['azi1'], units.degree)
    return {
        "speed": dist / time,
        "dist": dist,
        "time": time,
        "azi": azi
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Overlay gadgets on to GoPro MP4")

    parser.add_argument("input", help="Input MP4 file")
    parser.add_argument("--gpx", help="Use GPX file for location / alt / hr / cadence")
    parser.add_argument("--no-overlay", action="store_true", help="Only output the gadgets, don't overlay")
    parser.add_argument("output", help="Output MP4 file")

    args = parser.parse_args()

    gopro_timeseries = timeseries_from(args.input, units)
    print(f"GoPro Timeseries has {len(gopro_timeseries)} data points")

    from gpx import load_timeseries
    from ffmpeg import FFMPEGOverlay, FFMPEGGenerate

    if args.gpx:
        gpx_timeseries = load_timeseries(args.gpx, units)
        print(f"GPX Timeseries has {len(gpx_timeseries)} data points")
        wanted_timeseries = gpx_timeseries.clip_to(gopro_timeseries)
        print(f"GPX Timeseries overlap with GoPro - {len(wanted_timeseries)}")
        if not len(wanted_timeseries):
            raise ValueError("No overlap between GoPro and GPX file")
    else:
        wanted_timeseries = gopro_timeseries

    wanted_timeseries.process_deltas(calculate_speeds)
    wanted_timeseries.process(timeseries.process_ses("azi", lambda i: i.azi, alpha=0.2))

    ourdir = Path.home().joinpath(".gopro-graphics")
    ourdir.mkdir(exist_ok=True)

    with dbm.ndbm.open(str(ourdir.joinpath("tilecache.ndbm")), "c") as db:
        map_renderer = dbm_caching_renderer(db)

        datasource = TimeSeriesDataSource(wanted_timeseries)

        overlay = Overlay(datasource, map_renderer)

        if not args.no_overlay:
            ffmpeg = FFMPEGOverlay(input=args.input, output=args.output)
        else:
            ffmpeg = FFMPEGGenerate(output=args.output)

        with ffmpeg.generate() as writer:
            for time in datasource.timerange(step=timedelta(seconds=0.1)):
                datasource.time_is(time)
                writer.write(asarray(overlay.draw()).tobytes())
