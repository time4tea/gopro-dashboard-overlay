import datetime
import random

from .framemeta import FrameMeta
from .gpmd import GPSFix
from .point import Point
from .timeseries import Entry
from .timeunits import timeunits
from .units import units


class Random1D:

    def __init__(self, start, min_value=-2 ^ 31 - 1, rng=None):
        self.rng = rng or random.Random()
        self._n = start
        self._min_value = min_value

    def step(self):
        n = self.rng.random()

        if n < 0.45:
            self._n = self._n - 0.1
        elif n > 0.55:
            self._n = self._n + 0.1

        if self._n <= self._min_value:
            self._n = self._min_value

        return self._n


class Random2D:

    def __init__(self, start_point, step, rng=None):
        self.rng = rng or random.Random()
        self._point = start_point
        self._steps = [p * step for p in [
            Point(-1, -1), Point(-1, 0), Point(-1, 1),
            Point(0, -1), Point(0, 0), Point(0, 1),
            Point(1, -1), Point(1, 0), Point(1, 1)
        ]]

    def step(self):
        n = self.rng.randint(0, 8)
        self._point = self._point + self._steps[n]
        return self._point


def fake_framemeta(length: datetime.timedelta = datetime.timedelta(seconds=20),
                   step: datetime.timedelta = datetime.timedelta(seconds=0.1),
                   rng: random.Random = None,
                   point_step=0.001,
                   start_timestamp: int = 0) -> FrameMeta:
    rng = rng or random.Random()

    points = Random2D(Point(51.4972, -0.1499), point_step, rng=rng)
    speed = Random1D(10, rng=rng)
    cad = Random1D(50, rng=rng)
    grad = Random1D(23, rng=rng)
    hr = Random1D(100, rng=rng)
    alt = Random1D(1000, rng=rng)
    temp = Random1D(27, rng=rng)

    fm = FrameMeta()
    current_dt = datetime.datetime.fromtimestamp(start_timestamp, tz=datetime.timezone.utc)
    current_frame_time = timeunits(millis=0)

    end_dt = current_dt + length

    while current_dt <= end_dt:
        fm.add(
            current_frame_time,
            Entry(
                current_dt,
                timestamp=units.Quantity(current_frame_time.millis(), units.number),
                point=points.step(),
                speed=units.Quantity(speed.step(), units.mps),
                cad=units.Quantity(cad.step(), units.rpm),
                hr=units.Quantity(hr.step(), units.bpm),
                alt=units.Quantity(alt.step(), units.m),
                atemp=units.Quantity(temp.step(), units.celsius),
                grad=units.Quantity(grad.step()),
                gpsfix=GPSFix.LOCK_2D.value,
            )
        )
        current_dt = current_dt + step
        current_frame_time = current_frame_time + timeunits(seconds=step.total_seconds())
    return fm
