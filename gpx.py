import collections

import gpxpy
from pint import UnitRegistry

units = UnitRegistry()
units.define("bpm = beat / minute")
units.define("bps = beat / second")
units.define("rps = revolution / second")

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
        units.Quantity(gpx.alt, units.m),
        units.Quantity(gpx.hr, units.bpm),
        units.Quantity(gpx.cad, units.rpm),
        units.Quantity(gpx.atemp, units.celsius)
    )


if __name__ == "__main__":

    with open('/home/richja/Downloads/City_Loop.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    for point in [with_unit(p, units) for p in fudge(gpx)]:
        print(point)
