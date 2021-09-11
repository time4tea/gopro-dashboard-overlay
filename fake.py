import datetime

from overlayer import Extents, Journey
from point import Point
from timeseries import Entry
from units import units


class DataSource:

    def __init__(self):
        self.entry1 = Entry(
            datetime.datetime.now(),
            point=Point(51.4972, -0.1499),
            speed=units.Quantity(23.5, units.mps),
            cad=units.Quantity(113.0, units.rpm),
            hr=units.Quantity(67.0, units.bpm),
            alt=units.Quantity(1023.4, units.m)
        )
        self.entry2 = Entry(
            datetime.datetime.now(),
            point=Point(51.4072, -0.1699),
            speed=units.Quantity(23.5, units.mps),
            cad=units.Quantity(117.0, units.rpm),
            hr=units.Quantity(67.0, units.bpm),
            alt=units.Quantity(1023.4, units.m)
        )
        self.extents = Extents()
        self.extents.accept(self.entry1)
        self.extents.accept(self.entry2)
        self.journey = Journey()
        self.journey.accept(self.entry1)
        self.journey.accept(self.entry2)

    def datetime(self):
        return datetime.datetime.now()

    def point(self):
        return self.entry1.point

    def speed(self):
        return units.Quantity(23.5, units.mps)

    def azimuth(self):
        return units.Quantity(90, units.degrees)

    def cadence(self):
        return units.Quantity(113.0, units.rpm)

    def heart_rate(self):
        return units.Quantity(67.0, units.bpm)

    def altitude(self):
        return units.Quantity(1023.4, units.m)
