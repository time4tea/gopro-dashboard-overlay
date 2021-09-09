import collections
import datetime
from datetime import timedelta

from timeseries import Timeseries, Entry
from units import units

TUP = collections.namedtuple("TUP", "time lat lon alt hr cad atemp")


def test_creating_entry_from_namedtuple():
    some_tuple = TUP(time=datetime.datetime.fromtimestamp(1631178710), lat=10.0, lon=100.0, alt=-10, hr=100, cad=90,
                     atemp=17)
    entry = Entry(some_tuple.time, **some_tuple._asdict())
    assert entry.lat == 10.0


def test_creating_entry_from_namedtuple_ignores_non_numeric():
    some_tuple = TUP(time=datetime.datetime.fromtimestamp(1631178710), lat=10.0, lon=100.0, alt=-10, hr=100, cad=90,
                     atemp=17)
    entry = Entry(some_tuple.time, **some_tuple._asdict())
    assert entry.time is None


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
    ts = Timeseries()
    assert len(ts.items()) == 0
    assert ts.size == 0


def test_size():
    ts = Timeseries()
    ts.add(Entry(datetime.datetime.now(), a=1))
    ts.add(Entry(datetime.datetime.now(), a=1))
    assert ts.size == 2


def test_clipping():
    ts1 = Timeseries()
    ts2 = Timeseries()
    ts1.add(Entry(datetime.datetime.fromtimestamp(1)))
    ts1.add(Entry(datetime.datetime.fromtimestamp(2)))
    ts1.add(Entry(datetime.datetime.fromtimestamp(3)))
    ts1.add(Entry(datetime.datetime.fromtimestamp(3.5)))
    ts1.add(Entry(datetime.datetime.fromtimestamp(4)))
    ts1.add(Entry(datetime.datetime.fromtimestamp(5)))
    ts1.add(Entry(datetime.datetime.fromtimestamp(6)))

    ts2.add(Entry(datetime.datetime.fromtimestamp(2.5)))
    ts2.add(Entry(datetime.datetime.fromtimestamp(3)))
    ts2.add(Entry(datetime.datetime.fromtimestamp(4)))
    ts2.add(Entry(datetime.datetime.fromtimestamp(4.5)))

    clipped = ts1.clip_to(ts2)

    assert clipped.min == ts2.min
    assert clipped.max == ts2.max

    assert clipped.size == 5


def test_delta_processing():
    ts = Timeseries()
    entry_a = Entry(datetime.datetime.fromtimestamp(1), n=1)
    entry_b = Entry(datetime.datetime.fromtimestamp(2), n=2)
    ts.add(entry_a)
    ts.add(entry_b)

    ts.process_deltas(lambda a, b: {"d": b.n - a.n})

    assert entry_a.d == 1
    assert entry_b.d is None


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


def test_interpolating_quantity():
    dt1 = datetime.datetime.fromtimestamp(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(Entry(dt1, alt=units.Quantity(10, units.m)))
    ts.add(Entry(dt2, alt=units.Quantity(20, units.m)))

    assert ts.get(dt1 + timedelta(seconds=0.1)).alt == units.Quantity(11, units.m)
