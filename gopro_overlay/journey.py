from .point import Point


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


class Journey:

    def __init__(self):
        self.locations = []
        self.lat = MinMax("lat")
        self.lon = MinMax("lon")

    def accept(self, item):
        self.locations.append(item.point)
        self.lat.update(item.point.lat)
        self.lon.update(item.point.lon)

    @property
    def bounding_box(self):
        return Point(self.lat.min, self.lon.min), Point(self.lat.max, self.lon.max)
