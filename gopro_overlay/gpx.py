import collections

import gpxpy

from .point import Point
from .timeseries import Timeseries, Entry
from .units import units

GPX = collections.namedtuple("GPX", "time lat lon alt hr cad atemp")


def fudge(gpx):
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data = {
                    "time": point.time,
                    "lat": point.latitude,
                    "lon": point.longitude,
                    "alt": point.elevation,
                    "atemp": None,
                    "hr": None,
                    "cad": None
                }
                for element in point.extensions[0].iter():
                    tag = element.tag[element.tag.find("}") + 1:]
                    if tag in ("atemp", "hr", "cad"):
                        data[tag] = float(element.text)
                yield GPX(**data)


def with_unit(gpx, units):
    return GPX(
        gpx.time,
        gpx.lat,
        gpx.lon,
        units.Quantity(gpx.alt, units.m) if gpx.alt else None,
        units.Quantity(gpx.hr, units.bpm) if gpx.hr else None,
        units.Quantity(gpx.cad, units.rpm) if gpx.cad else None,
        units.Quantity(gpx.atemp, units.celsius) if gpx.atemp else None
    )


def load(filepath, units):
    with open(filepath, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    return [with_unit(p, units) for p in fudge(gpx)]


def load_timeseries(filepath, units):
    gpx = load(filepath, units)

    gpx_timeseries = Timeseries()

    points = [
        Entry(
            point.time,
            point=Point(point.lat, point.lon),
            alt=point.alt,
            hr=point.hr,
            cad=point.cad,
            atemp=point.atemp,
        )
        for point in gpx
    ]

    gpx_timeseries.add(*points)

    return gpx_timeseries


if __name__ == "__main__":

    for point in load('/home/richja/Downloads/City_Loop.gpx', units):
        print(point)
