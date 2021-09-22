from geographiclib.geodesic import Geodesic

from .units import units


class PrivacyZone:

    def __init__(self, point, dist):
        self.point = point
        self.dist = dist

    def encloses(self, point):
        actual = units.Quantity(
            abs(Geodesic.WGS84.Inverse(self.point.lat, self.point.lon, point.lat, point.lon)['s12']),
            units.m
        )
        return actual <= self.dist

    def __str__(self):
        return f"PrivacyZone: {self.dist} around {self.point}"


class NoPrivacyZone:
    def encloses(self, point):
        return False
