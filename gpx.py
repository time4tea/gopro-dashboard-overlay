import collections

import gpxpy

from units import units

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


def load(filepath, units):
    with open(filepath, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    return [with_unit(p, units) for p in fudge(gpx)]


if __name__ == "__main__":

    for point in load('/home/richja/Downloads/City_Loop.gpx', units):
        print(point)
