import collections
import datetime
from datetime import timedelta

from gopro_overlay import fake
from gopro_overlay.gpmd import Point
from gopro_overlay.timeseries import Timeseries, Entry, Window
from gopro_overlay.timeseries_process import process_ses
from gopro_overlay.units import units, metres

TUP = collections.namedtuple("TUP", "time lat lon alt hr cad atemp")


def test_creating_entry_from_namedtuple():
    some_tuple = TUP(time=datetime_of(1631178710), lat=10.0, lon=100.0, alt=-10, hr=100, cad=90,
                     atemp=17)
    entry = Entry(some_tuple.time, **some_tuple._asdict())
    assert entry.lat == 10.0


def test_creating_entry_from_namedtuple_ignores_non_numeric():
    some_tuple = TUP(time=datetime_of(1631178710), lat=10.0, lon=100.0, alt=-10, hr=100, cad=90,
                     atemp=17)
    entry = Entry(some_tuple.time, **some_tuple._asdict())
    assert entry.time is None


def test_interpolating_entry():
    dt1 = datetime_of(1631178710)
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
    dt = datetime_of(1631178710)
    dt1 = dt + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(Entry(dt, point=Point(lat=1.0, lon=1.0), alt=12))
    ts.add(Entry(dt1, point=Point(lat=2.0, lon=1.0), alt=12))
    assert ts.get(dt).point.lat == 1.0
    assert ts.get(dt1).point.lat == 2.0


def test_iterating_empty_timeseries():
    ts = Timeseries()
    assert len(ts.items()) == 0
    assert len(ts) == 0


def test_size():
    ts = Timeseries()
    ts.add(Entry(datetime_of(1), a=1))
    ts.add(Entry(datetime_of(2), a=1))
    assert len(ts) == 2


def test_clipping():
    ts1 = Timeseries()
    ts2 = Timeseries()
    ts1.add(Entry(datetime_of(1)))
    ts1.add(Entry(datetime_of(2)))
    ts1.add(Entry(datetime_of(3)))
    ts1.add(Entry(datetime_of(3.5)))
    ts1.add(Entry(datetime_of(4)))
    ts1.add(Entry(datetime_of(5)))
    ts1.add(Entry(datetime_of(6)))

    ts2.add(Entry(datetime_of(2.5)))
    ts2.add(Entry(datetime_of(3)))
    ts2.add(Entry(datetime_of(4)))
    ts2.add(Entry(datetime_of(4.5)))

    clipped = ts1.clip_to(ts2)

    assert clipped.min == datetime_of(2)
    assert clipped.max == datetime_of(5)

    assert len(clipped) == 5


def test_delta_processing():
    ts = Timeseries()
    entry_a = Entry(datetime_of(1), n=1)
    entry_b = Entry(datetime_of(2), n=2)
    ts.add(entry_a)
    ts.add(entry_b)

    ts.process_deltas(lambda a, b, c: {"d": b.n - a.n, "c": c})

    assert entry_a.d == 1
    assert entry_b.d is None
    assert entry_a.c == 1
    assert entry_b.c is None


def datetime_of(i):
    return datetime.datetime.fromtimestamp(i)


def test_processing_with_simple_exp_smoothing():
    ts = Timeseries()
    ts.add(
        Entry(datetime_of(1), n=3),
        Entry(datetime_of(2), n=5),
        Entry(datetime_of(3), n=9),
        Entry(datetime_of(4), n=20),
    )
    ts.process(process_ses("ns", lambda i: i.n, alpha=0.4))

    assert ts.get(datetime_of(1)).ns == 3.0
    assert ts.get(datetime_of(2)).ns == 3.0
    assert ts.get(datetime_of(3)).ns == 3.8
    assert ts.get(datetime_of(4)).ns == 5.88


def test_adding_multiple_items():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(
        Entry(dt1, point=Point(lat=3.0, lon=1.0), alt=12),
        Entry(dt2, point=Point(lat=2.0, lon=1.0), alt=12)
    )
    assert ts.get(dt1).point.lat == 3.0
    assert ts.get(dt2).point.lat == 2.0


def test_iterates_in_datetime_order():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=2)
    dt3 = dt1 + timedelta(seconds=4)
    ts = Timeseries()
    ts.add(Entry(dt3, point=Point(lat=3.0, lon=1.0), alt=12))
    ts.add(Entry(dt2, point=Point(lat=2.0, lon=1.0), alt=12))
    ts.add(Entry(dt1, point=Point(lat=1.0, lon=1.0), alt=12))

    iterator = iter(ts.items())
    assert next(iterator).point.lat == 1.0
    assert next(iterator).point.lat == 2.0
    assert next(iterator).point.lat == 3.0


def test_getting_point_before_start_throws():
    import pytest
    ts = Timeseries()
    dt1 = datetime_of(1631178710)
    ts.add(Entry(dt1, lat=1.0, lon=1.0, alt=12))
    with pytest.raises(ValueError):
        ts.get(dt1 - timedelta(seconds=1))


def test_getting_point_after_end_throws():
    import pytest
    ts = Timeseries()
    dt1 = datetime_of(1631178710)
    ts.add(Entry(dt1, lat=1.0, lon=1.0, alt=12))
    with pytest.raises(ValueError):
        ts.get(dt1 + timedelta(seconds=1))


def test_getting_intermediate_point_gets_interpolated():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    dt3 = dt1 + timedelta(seconds=2)
    ts = Timeseries()
    ts.add(Entry(dt1, point=Point(lat=1.0, lon=1.0), alt=12))
    ts.add(Entry(dt2, point=Point(lat=2.0, lon=1.0), alt=12))
    ts.add(Entry(dt3, point=Point(lat=3.0, lon=1.0), alt=12))

    assert ts.get(dt1).point.lat == 1.0
    assert ts.get(dt2).point.lat == 2.0
    assert ts.get(dt3).point.lat == 3.0
    assert ts.get(dt1 + timedelta(seconds=0.0)).point.lat == 1.0
    assert ts.get(dt1 + timedelta(seconds=0.1)).point.lat == 1.1
    assert ts.get(dt1 + timedelta(seconds=0.2)).point.lat == 1.2
    assert ts.get(dt1 + timedelta(seconds=0.3)).point.lat == 1.3
    assert ts.get(dt1 + timedelta(seconds=0.4)).point.lat == 1.4
    assert ts.get(dt1 + timedelta(seconds=0.5)).point.lat == 1.5
    assert ts.get(dt1 + timedelta(seconds=0.6)).point.lat == 1.6
    assert ts.get(dt1 + timedelta(seconds=0.7)).point.lat == 1.7
    assert ts.get(dt1 + timedelta(seconds=0.8)).point.lat == 1.8
    assert ts.get(dt1 + timedelta(seconds=0.9)).point.lat == 1.9
    assert ts.get(dt1 + timedelta(seconds=1.0)).point.lat == 2.0
    assert ts.get(dt1 + timedelta(seconds=1.1)).point.lat == 2.1
    assert ts.get(dt1 + timedelta(seconds=1.2)).point.lat == 2.2
    assert ts.get(dt1 + timedelta(seconds=1.3)).point.lat == 2.3
    assert ts.get(dt1 + timedelta(seconds=1.4)).point.lat == 2.4
    assert ts.get(dt1 + timedelta(seconds=1.5)).point.lat == 2.5
    assert ts.get(dt1 + timedelta(seconds=1.6)).point.lat == 2.6
    assert ts.get(dt1 + timedelta(seconds=1.7)).point.lat == 2.7
    assert ts.get(dt1 + timedelta(seconds=1.8)).point.lat == 2.8
    assert ts.get(dt1 + timedelta(seconds=1.9)).point.lat == 2.9
    assert ts.get(dt1 + timedelta(seconds=2.0)).point.lat == 3.0


def test_interpolating_quantity():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(Entry(dt1, alt=metres(10)))
    ts.add(Entry(dt2, alt=metres(20)))

    assert ts.get(dt1 + timedelta(seconds=0.1)).alt == metres(11)


def test_filling_missing_entries():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    dt3 = dt2 + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(Entry(dt1, alt=metres(10)))
    # no entry for dt2
    ts.add(Entry(dt3, alt=metres(30)))

    assert dt1 in ts.dates
    assert dt2 not in ts.dates

    filled = ts.backfill(timedelta(seconds=1))
    assert filled == 1
    assert dt2 in ts.dates
    assert ts.get(dt2).alt.magnitude == 20


def test_taking_a_view():
    ts = fake.fake_timeseries(timedelta(minutes=10), step=timedelta(seconds=1))

    window = Window(ts, timedelta(minutes=1), samples=100, key=lambda e: e.alt, missing=0)

    view = window.view(ts.min)

    assert view.version == 1
    data = view.data
    assert len(data) == 100
    assert data[0] == 0
    assert data[50].units == units.meter
    assert data[99].units == units.meter

    view = window.view(ts.max)
    assert view.version == 2


def test_missing_window_entries():
    ts = fake.fake_timeseries(timedelta(minutes=10), step=timedelta(seconds=1))

    window = Window(ts, timedelta(minutes=1), samples=100, key=lambda e: e.bob, fmt=lambda v: v.magnitude, missing=0)

    window.view(ts.min)


def test_stepping_through_time():
    ts = fake.fake_timeseries(timedelta(minutes=10), step=timedelta(seconds=1))
    stepper = ts.stepper(timedelta(minutes=1))

    steps = []

    # its exactly 10 mins long, so we have 0,1,2,3,4,5,6,7,8,9,10 mins.
    assert len(stepper) == 11

    for step in stepper.steps():
        steps.append(step)

    assert len(steps) == 11
    assert steps[0] == datetime_of(0)
    assert steps[1] == datetime_of(60)
    assert steps[10] == datetime_of(60 * 10)
