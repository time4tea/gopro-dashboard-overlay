import math
from typing import List

from .gpmd import GPS_FIXED_VALUES
from .point import Point, BoundingBox


class MinMax:

    def __init__(self, name):
        self._items = []
        self._name = name

    @property
    def name(self):
        return self._name

    def update(self, new):
        if new is not None:
            self._items.append(new)

    def __len__(self):
        return len(self._items)

    @property
    def min(self):
        return min(self._items)

    @property
    def max(self):
        return max(self._items)

    def __str__(self):
        return f"{self.name}: min:{self.min} max:{self.max}"


class Extents:

    def __init__(self):
        self.lat = MinMax("lat")
        self.lon = MinMax("lon")
        self.velocity = MinMax("velocity")
        self.altitude = MinMax("altitude")
        self.cadence = MinMax("cadence")
        self.hr = MinMax("hr")

    def accept(self, item):
        self.velocity.update(item.speed)
        self.altitude.update(item.alt)
        self.cadence.update(item.cad)
        self.hr.update(item.hr)


MIN_BOX_SIZE = 0.0001


class Journey:

    def __init__(self):
        self.locations: List[Point] = []
        self.lat = MinMax("lat")
        self.lon = MinMax("lon")
        self.badlat = MinMax("badlat")
        self.badlon = MinMax("badlon")

    def accept(self, item):
        if item.gpsfix in GPS_FIXED_VALUES:
            self.locations.append(item.point)
            self.lat.update(item.point.lat)
            self.lon.update(item.point.lon)
        else:
            self.badlat.update(item.point.lat)
            self.badlon.update(item.point.lon)

    @property
    def bounding_box(self) -> BoundingBox:
        lat = self.lat if self.lat else self.badlat
        lon = self.lon if self.lon else self.badlon

        if math.dist([lat.min, lon.min], [lat.max, lon.max]) < MIN_BOX_SIZE:
            return BoundingBox(Point(lat.min, lon.min), Point(lat.min + MIN_BOX_SIZE, lon.min + MIN_BOX_SIZE))

        return BoundingBox(Point(lat.min, lon.min), Point(lat.max, lon.max))
