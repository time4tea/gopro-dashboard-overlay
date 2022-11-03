import collections
import gzip

import gpxpy

from .gpmd import GPSFix
from .point import Point
from .timeseries import Timeseries, Entry

GPX = collections.namedtuple("GPX", "time lat lon alt hr cad atemp power")


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
                    "cad": None,
                    "power": None
                }
                for extension in point.extensions:
                    for element in extension.iter():
                        tag = element.tag[element.tag.find("}") + 1:]
                        if tag in ("atemp", "hr", "cad", "power"):
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
        units.Quantity(gpx.atemp, units.celsius) if gpx.atemp else None,
        units.Quantity(gpx.power, units.watt) if gpx.power else None
    )


def load(filepath, units):
    if filepath.endswith(".gz"):
        with gzip.open(filepath, 'rb') as gpx_file:
            return load_xml(gpx_file, units)
    else:
        with open(filepath, 'r') as gpx_file:
            return load_xml(gpx_file, units)


def load_xml(file_or_str, units):
    gpx = gpxpy.parse(file_or_str)

    return [with_unit(p, units) for p in fudge(gpx)]


def gpx_to_timeseries(gpx):
    gpx_timeseries = Timeseries()

    points = [
        Entry(
            point.time,
            point=Point(point.lat, point.lon),
            alt=point.alt,
            hr=point.hr,
            cad=point.cad,
            atemp=point.atemp,
            power=point.power,
            # we should set the gps fix or Journey.accept() will skip the point:
            gpsfix=GPSFix.LOCK_3D.value,
        )
        for point in gpx
    ]

    gpx_timeseries.add(*points)

    return gpx_timeseries


def load_timeseries(filepath, units):
    return gpx_to_timeseries(load(filepath, units))
