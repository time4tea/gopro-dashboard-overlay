import datetime
import random

from .point import Point
from .timeseries import Entry, Timeseries
from .units import units


class Random1D:

    def __init__(self, start, min_value=-2 ^ 31 - 1):
        self._n = start
        self._min_value = min_value

    def step(self):
        n = random.random()

        if n < 0.45:
            self._n = self._n - 1
        elif n > 0.55:
            self._n = self._n + 1

        if self._n <= self._min_value:
            self._n = self._min_value

        return self._n


class Random2D:

    def __init__(self, start_point, step):
        self._point = start_point
        self._steps = [p * step for p in [
            Point(-1, -1), Point(-1, 0), Point(-1, 1),
            Point(0, -1), Point(0, 0), Point(0, 1),
            Point(1, -1), Point(1, 0), Point(1, 1)
        ]]

    def step(self):
        n = random.randint(0, 8)
        self._point = self._point + self._steps[n]
        return self._point


def fake_timeseries(length: datetime.timedelta = datetime.timedelta(seconds=20),
                    step: datetime.timedelta = datetime.timedelta(seconds=0.1)):
    points = Random2D(Point(51.4972, -0.1499), 0.001)
    speed = Random1D(10)
    cad = Random1D(50)
    grad = Random1D(23)
    hr = Random1D(100)
    alt = Random1D(1000)
    temp = Random1D(27)

    ts = Timeseries()
    current_dt = datetime.datetime.fromtimestamp(0)
    end_dt = current_dt + length

    while current_dt < end_dt:
        ts.add(
            Entry(
                current_dt,
                point=points.step(),
                speed=units.Quantity(speed.step(), units.mps),
                cad=units.Quantity(cad.step(), units.rpm),
                hr=units.Quantity(hr.step(), units.bpm),
                alt=units.Quantity(alt.step(), units.m),
                atemp=units.Quantity(temp.step(), units.celsius),
                grad=units.Quantity(grad.step())
            )
        )
        current_dt = current_dt + step

    return ts
