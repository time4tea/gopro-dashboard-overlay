import dbm
from datetime import datetime
from pathlib import Path

from geo import dbm_caching_renderer
from gpmd import timeseries_from
from image import Overlay

from pint import UnitRegistry
from numpy import asarray

units = UnitRegistry()


class TimeSeriesDataSource:

    def __init__(self, timeseries):
        self._timeseries = timeseries
        self._time = timeseries.min
        self._gps = self._timeseries.get(self._time, "gps")

    def timerange(self):
        start = self._timeseries.min
        stop = self._timeseries.max
        step = self._timeseries.resolution
        count = 0
        while True:
            temp = float(start + count * step)
            if temp >= stop:
                break
            yield temp
            count += 1

    def time_is(self, time):
        self._time = time
        self._gps = self._timeseries.get(self._time, "gps")

    def datetime(self):
        return datetime.fromtimestamp(self._time)

    def lat(self):
        if self._gps is not None:
            return self._gps.lat

    def lon(self):
        if self._gps is not None:
            return self._gps.lon

    def speed(self):
        if self._gps is not None:
            return units.Quantity(self._gps.speed, units.mps)
        else:
            return units.Quantity(0, units.mps)


if __name__ == "__main__":

    from vidgear.gears import WriteGear

    filename = "GH010064"

    timeseries = timeseries_from(f"/data/richja/gopro/{filename}.MP4", resolution=0.10)

    print(f"Timeseries has {timeseries.size} data points")

    ourdir = Path.home().joinpath(".gopro-graphics")
    ourdir.mkdir(exist_ok=True)

    with dbm.ndbm.open(str(ourdir.joinpath("tilecache.ndbm")), "c") as db:
        map_renderer = dbm_caching_renderer(db)

        datasource = TimeSeriesDataSource(timeseries)
        overlay = Overlay(datasource, map_renderer)
        output_params = {"-input_framerate": 10, "-r": 30}
        writer = WriteGear(output_filename=f"{filename}-overlay.mp4", logging=True, **output_params)

        for time in datasource.timerange():
            datasource.time_is(time)
            writer.write(asarray(overlay.draw()))

