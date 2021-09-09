import dbm
from datetime import datetime, timedelta
from pathlib import Path

from numpy import asarray

import timeseries
from geo import dbm_caching_renderer
from gpmd import timeseries_from
from image import Overlay
from timeseries import Timeseries
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
        if self._entry is not None:
            return self._entry.lat

    def lon(self):
        if self._entry is not None:
            return self._entry.lon

    def speed(self):
        if self._entry is not None:
            return units.Quantity(self._entry.speed, units.mps)
        else:
            return units.Quantity(0, units.mps)


if __name__ == "__main__":

    from vidgear.gears import WriteGear

    filename = "GH010064"

    gopro_timeseries = timeseries_from(f"/data/richja/gopro/{filename}.MP4")

    from gpx import load

    gpx = load("/home/richja/Downloads/City_Loop.gpx", units)

    gpx_timeseries = Timeseries()

    points = [
        timeseries.Entry(
            point.time,
            lat=point.lat,
            lon=point.lon,
            alt=point.alt,
            hr=point.hr,
            cad=point.cad
        )
        for point in gpx
    ]

    gpx_timeseries.add(*points)

    wanted_timeseries = gpx_timeseries.clip_to(gopro_timeseries)

    print(f"GPS Timeseries has {gopro_timeseries.size} data points")
    print(f"GPX Timeseries has {gpx_timeseries.size} data points")

    ourdir = Path.home().joinpath(".gopro-graphics")
    ourdir.mkdir(exist_ok=True)

    with dbm.ndbm.open(str(ourdir.joinpath("tilecache.ndbm")), "c") as db:
        map_renderer = dbm_caching_renderer(db)

        datasource = TimeSeriesDataSource(wanted_timeseries)
        overlay = Overlay(datasource, map_renderer)
        output_params = {"-input_framerate": 10, "-r": 30}
        writer = WriteGear(output_filename=f"{filename}-overlay.mp4", logging=True, **output_params)

        for time in datasource.timerange(step=timedelta(seconds=0.1)):
            datasource.time_is(time)
            writer.write(asarray(overlay.draw()))
