from pint import Quantity

from gopro_overlay.point import Point
from gopro_overlay.units import units


def correct_altitude(point: Point, alt: Quantity):
    pass


def test_altitude_correction():
    assert correct_altitude(
        point=Point(lat=46.166195, lon=-94.405447),
        alt=units.Quantity(100, units.m)
    ) == units.Quantity(50, units.m)
