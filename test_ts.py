import bisect
import datetime
from datetime import timedelta


class Timeseries:

    def __init__(self):
        self.entries = {}
        self.dates = []

    def _update(self):
        self.dates = sorted(list(self.entries.keys()))

    def add(self, *entries):
        for e in entries:
            self.entries[e.dt] = e
        self._update()

    def get(self, dt):
        if not self.dates or dt < self.dates[0]:
            raise ValueError("Date is before start")
        if dt > self.dates[-1]:
            raise ValueError("Date is after end")
        if dt in self.entries:
            return self.entries[dt]
        else:
            greater_idx = bisect.bisect_left(self.dates, dt)
            lesser_idx = greater_idx - 1

            return self.entries[self.dates[lesser_idx]].interpolate(self.entries[self.dates[greater_idx]], dt)

    def items(self):
        return [self.entries[k] for k in self.dates]


class Entry:

    def __init__(self, dt, **kwargs):
        self.dt = dt
        self.items = dict(**kwargs)

    def __getattr__(self, item):
        return self.items.get(item, None)

    def interpolate(self, other, dt):
        if self.dt == other.dt:
            raise ValueError("Cannot interpolate between equal points")
        if self.dt > other.dt:
            raise ValueError("Lower point must be first")
        if dt < self.dt:
            raise ValueError("Wanted point before lower")
        if dt > other.dt:
            raise ValueError("Wanted point after other")

        if dt == self.dt:
            return self
        elif dt == other.dt:
            return other

        range = (other.dt - self.dt) / timedelta(milliseconds=1)
        point = (dt - self.dt) / timedelta(milliseconds=1)

        position = point / range

        items = {}
        for key in self.items.keys():
            start = self.items[key]
            end = other.items[key]
            diff = end - start
            interp = start + (position * diff)
            items[key] = interp

        return Entry(dt, **items)


def test_interpolating_entry():
    dt1 = datetime.datetime.fromtimestamp(1631178710)
    dt2 = dt1 + timedelta(seconds=1)

    point = dt1 + ((dt2 - dt1) / 2)

    e1 = Entry(dt1, lat=1.0, lon=10)
    e2 = Entry(dt2, lat=2.0, lon=20)

    assert e1.interpolate(e2, dt1).lat == 1.0
    assert e1.interpolate(e2, dt1).lon == 10.0
    assert e1.interpolate(e2, dt2).lat == 2.0
    assert e1.interpolate(e2, dt2).lon == 20.0
    assert e1.interpolate(e2, point).lat == 1.5
    assert e1.interpolate(e2, point).lon == 15


def test_putting_in_a_point_gets_back_that_point():
    dt = datetime.datetime.fromtimestamp(1631178710)
    dt1 = dt + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(Entry(dt, lat=1.0, lon=1.0, alt=12))
    ts.add(Entry(dt1, lat=2.0, lon=1.0, alt=12))
    assert ts.get(dt).lat == 1.0
    assert ts.get(dt1).lat == 2.0


def test_iterating_empty_timeseries():
    assert len(Timeseries().items()) == 0


def test_adding_multiple_items():
    dt1 = datetime.datetime.fromtimestamp(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(
        Entry(dt1, lat=3.0, lon=1.0, alt=12),
        Entry(dt2, lat=2.0, lon=1.0, alt=12)
    )
    assert ts.get(dt1).lat == 3.0
    assert ts.get(dt2).lat == 2.0


def test_iterates_in_datetime_order():
    dt1 = datetime.datetime.fromtimestamp(1631178710)
    dt2 = dt1 + timedelta(seconds=2)
    dt3 = dt1 + timedelta(seconds=4)
    ts = Timeseries()
    ts.add(Entry(dt3, lat=3.0, lon=1.0, alt=12))
    ts.add(Entry(dt2, lat=2.0, lon=1.0, alt=12))
    ts.add(Entry(dt1, lat=1.0, lon=1.0, alt=12))

    iterator = iter(ts.items())
    assert next(iterator).lat == 1.0
    assert next(iterator).lat == 2.0
    assert next(iterator).lat == 3.0


def test_getting_point_before_start_throws():
    import pytest
    ts = Timeseries()
    dt1 = datetime.datetime.fromtimestamp(1631178710)
    ts.add(Entry(dt1, lat=1.0, lon=1.0, alt=12))
    with pytest.raises(ValueError):
        ts.get(dt1 - timedelta(seconds=1))


def test_getting_point_after_end_throws():
    import pytest
    ts = Timeseries()
    dt1 = datetime.datetime.fromtimestamp(1631178710)
    ts.add(Entry(dt1, lat=1.0, lon=1.0, alt=12))
    with pytest.raises(ValueError):
        ts.get(dt1 + timedelta(seconds=1))


def test_getting_intermediate_point_gets_interpolated():
    dt1 = datetime.datetime.fromtimestamp(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    dt3 = dt1 + timedelta(seconds=2)
    ts = Timeseries()
    ts.add(Entry(dt1, lat=1.0, lon=1.0, alt=12))
    ts.add(Entry(dt2, lat=2.0, lon=1.0, alt=12))
    ts.add(Entry(dt3, lat=3.0, lon=1.0, alt=12))

    assert ts.get(dt1).lat == 1.0
    assert ts.get(dt2).lat == 2.0
    assert ts.get(dt3).lat == 3.0
    assert ts.get(dt1 + timedelta(seconds=0.0)).lat == 1.0
    assert ts.get(dt1 + timedelta(seconds=0.1)).lat == 1.1
    assert ts.get(dt1 + timedelta(seconds=0.2)).lat == 1.2
    assert ts.get(dt1 + timedelta(seconds=0.3)).lat == 1.3
    assert ts.get(dt1 + timedelta(seconds=0.4)).lat == 1.4
    assert ts.get(dt1 + timedelta(seconds=0.5)).lat == 1.5
    assert ts.get(dt1 + timedelta(seconds=0.6)).lat == 1.6
    assert ts.get(dt1 + timedelta(seconds=0.7)).lat == 1.7
    assert ts.get(dt1 + timedelta(seconds=0.8)).lat == 1.8
    assert ts.get(dt1 + timedelta(seconds=0.9)).lat == 1.9
    assert ts.get(dt1 + timedelta(seconds=1.0)).lat == 2.0
    assert ts.get(dt1 + timedelta(seconds=1.1)).lat == 2.1
    assert ts.get(dt1 + timedelta(seconds=1.2)).lat == 2.2
    assert ts.get(dt1 + timedelta(seconds=1.3)).lat == 2.3
    assert ts.get(dt1 + timedelta(seconds=1.4)).lat == 2.4
    assert ts.get(dt1 + timedelta(seconds=1.5)).lat == 2.5
    assert ts.get(dt1 + timedelta(seconds=1.6)).lat == 2.6
    assert ts.get(dt1 + timedelta(seconds=1.7)).lat == 2.7
    assert ts.get(dt1 + timedelta(seconds=1.8)).lat == 2.8
    assert ts.get(dt1 + timedelta(seconds=1.9)).lat == 2.9
    assert ts.get(dt1 + timedelta(seconds=2.0)).lat == 3.0
