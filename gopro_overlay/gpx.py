import collections
import gzip
from pathlib import Path
from typing import List

import gpxpy

from .gpmf import GPSFix
from .point import Point
from .timeseries import Timeseries, Entry

GPX = collections.namedtuple("GPX", "time lat lon alt hr cad atemp power speed custom_fields custom_metadata")


def fudge(gpx):
    metadata = dict((m.tag, m.text) for m in gpx.metadata_extensions)
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
                    "power": None,
                    "speed": None,
                    "custom_fields": {},
                    "custom_metadata": metadata
                }
                for extension in point.extensions:
                    for element in extension.iter():
                        tag = element.tag[element.tag.find("}") + 1:]
                        if tag in ("atemp", "hr", "cad", "power", "speed"):
                            data[tag] = float(element.text)
                        else:
                            data["custom_fields"][tag] = element.text
                yield GPX(**data)


def with_unit(gpx, units):
    return GPX(
        gpx.time,
        gpx.lat,
        gpx.lon,
        units.Quantity(gpx.alt, units.m) if gpx.alt is not None else None,
        units.Quantity(gpx.hr, units.bpm) if gpx.hr is not None else None,
        units.Quantity(gpx.cad, units.rpm) if gpx.cad is not None else None,
        units.Quantity(gpx.atemp, units.celsius) if gpx.atemp is not None else None,
        units.Quantity(gpx.power, units.watt) if gpx.power is not None else None,
        units.Quantity(gpx.speed, units.mps) if gpx.speed is not None else None,
        gpx.custom_fields,
        gpx.custom_metadata
    )


def load(filepath: Path, units):
    if filepath.suffix == ".gz":
        with gzip.open(filepath, 'rb') as gpx_file:
            return load_xml(gpx_file, units)
    else:
        with filepath.open('r') as gpx_file:
            return load_xml(gpx_file, units)


def load_xml(file_or_str, units) -> List[GPX]:
    gpx = gpxpy.parse(file_or_str)

    return [with_unit(p, units) for p in fudge(gpx)]


def gpx_to_timeseries(gpx: List[GPX], units):
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
            speed=point.speed,
            packet=units.Quantity(index),
            packet_index=units.Quantity(0),
            # we should set the gps fix or Journey.accept() will skip the point:
            gpsfix=GPSFix.LOCK_3D.value,
            gpslock=units.Quantity(GPSFix.LOCK_3D.value),

            custom_fields=point.custom_fields,
            custom_metadata=point.custom_metadata
        )
        for index, point in enumerate(gpx)
    ]

    gpx_timeseries.add(*points)

    return gpx_timeseries


def load_timeseries(filepath: Path, units) -> Timeseries:
    return gpx_to_timeseries(load(filepath, units), units)
