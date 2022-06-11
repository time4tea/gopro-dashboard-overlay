import collections
from datetime import timedelta

from gopro_overlay import fake
from gopro_overlay.entry import Entry
from gopro_overlay.framemeta import FrameMeta, Window
from gopro_overlay.point import Point
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import metres, units
from tests.test_timeseries import datetime_of

TUP = collections.namedtuple("TUP", "time lat lon alt hr cad atemp")


def test_creating_entry_from_namedtuple():
    some_tuple = TUP(time=datetime_of(1631178710), lat=10.0, lon=100.0, alt=-10, hr=100, cad=90,
                     atemp=17)
    entry = Entry(some_tuple.time, **some_tuple._asdict())
    assert entry.lat == 10.0


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
    fm = FrameMeta()
    fm.add(timeunits(seconds=1), Entry(datetime_of(0), point=Point(lat=1.0, lon=1.0), alt=12))
    fm.add(timeunits(seconds=2), Entry(datetime_of(1), point=Point(lat=2.0, lon=1.0), alt=12))
    assert fm.get(timeunits(seconds=1)).point.lat == 1.0
    assert fm.get(timeunits(seconds=2)).point.lat == 2.0


def test_iterating_empty():
    fm = FrameMeta()
    assert len(fm.items()) == 0
    assert len(fm) == 0


def test_size():
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(1), a=1))
    fm.add(timeunits(seconds=1), Entry(datetime_of(2), a=1))
    assert len(fm) == 2


def test_iterates_in_frame_time_order_not_insertion_order():
    fm = FrameMeta()
    fm.add(timeunits(seconds=2), Entry(datetime_of(0), point=Point(lat=3.0, lon=1.0), alt=12))
    fm.add(timeunits(seconds=1), Entry(datetime_of(1), point=Point(lat=2.0, lon=1.0), alt=12))
    fm.add(timeunits(seconds=0), Entry(datetime_of(2), point=Point(lat=1.0, lon=1.0), alt=12))

    iterator = iter(fm.items())
    assert next(iterator).point.lat == 1.0
    assert next(iterator).point.lat == 2.0
    assert next(iterator).point.lat == 3.0


def test_getting_point_before_start_returns_first_item():
    '''sometimes the first metadata item comes after the first frame, so bodge it'''
    fm = FrameMeta()
    fm.add(timeunits(seconds=1), Entry(datetime_of(0), lat=1.0))
    fm.add(timeunits(seconds=2), Entry(datetime_of(0), lat=2.0))

    assert fm.get(timeunits(seconds=0)).lat == 1.0


def test_getting_point_after_end_returns_last_item():
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(0), lat=0.0))
    fm.add(timeunits(seconds=1), Entry(datetime_of(0), lat=1.0))
    assert fm.get(timeunits(seconds=2)).lat == 1.0


def test_interpolating_entries_with_same_date_returns_other():
    # this can happen with time lapse entries
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(0), lat=1.0))
    fm.add(timeunits(seconds=2), Entry(datetime_of(0), lat=2.0))

    assert fm.get(timeunits(seconds=1)).lat == 2.0


def test_getting_intermediate_point_gets_interpolated():
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(0), lat=1.0))
    fm.add(timeunits(seconds=1), Entry(datetime_of(1), lat=2.0))
    fm.add(timeunits(seconds=2), Entry(datetime_of(2), lat=3.0))

    assert fm.get(timeunits(seconds=0)).lat == 1.0
    assert fm.get(timeunits(seconds=1)).lat == 2.0
    assert fm.get(timeunits(seconds=2)).lat == 3.0
    assert fm.get(timeunits(seconds=0.0)).lat == 1.0
    assert fm.get(timeunits(seconds=0.1)).lat == 1.1
    assert fm.get(timeunits(seconds=0.2)).lat == 1.2
    assert fm.get(timeunits(seconds=0.3)).lat == 1.3
    assert fm.get(timeunits(seconds=0.4)).lat == 1.4
    assert fm.get(timeunits(seconds=0.5)).lat == 1.5
    assert fm.get(timeunits(seconds=0.6)).lat == 1.6
    assert fm.get(timeunits(seconds=0.7)).lat == 1.7
    assert fm.get(timeunits(seconds=0.8)).lat == 1.8
    assert fm.get(timeunits(seconds=0.9)).lat == 1.9
    assert fm.get(timeunits(seconds=1.0)).lat == 2.0
    assert fm.get(timeunits(seconds=1.1)).lat == 2.1
    assert fm.get(timeunits(seconds=1.2)).lat == 2.2
    assert fm.get(timeunits(seconds=1.3)).lat == 2.3
    assert fm.get(timeunits(seconds=1.4)).lat == 2.4
    assert fm.get(timeunits(seconds=1.5)).lat == 2.5
    assert fm.get(timeunits(seconds=1.6)).lat == 2.6
    assert fm.get(timeunits(seconds=1.7)).lat == 2.7
    assert fm.get(timeunits(seconds=1.8)).lat == 2.8
    assert fm.get(timeunits(seconds=1.9)).lat == 2.9
    assert fm.get(timeunits(seconds=2.0)).lat == 3.0


def test_interpolating_quantity():
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(0), alt=metres(10)))
    fm.add(timeunits(seconds=1), Entry(datetime_of(1), alt=metres(20)))

    assert fm.get(timeunits(seconds=0.1)).alt == metres(11)


def test_taking_a_view():
    fm = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1))

    window = Window(fm, timeunits(minutes=1), samples=100, key=lambda e: e.alt, missing=0)

    view = window.view(fm.min)

    assert view.version == 1
    data = view.data
    assert len(data) == 100
    assert data[0] == 0
    assert data[50].units == units.meter
    assert data[99].units == units.meter

    view = window.view(fm.max)
    assert view.version == 2


def test_missing_window_entries():
    ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1))

    window = Window(ts, timeunits(minutes=1), samples=100, key=lambda e: e.bob, fmt=lambda v: v.magnitude, missing=0)

    window.view(ts.min)


def test_stepping_through_time():
    ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1))
    stepper = ts.stepper(timeunits(minutes=1))

    steps = []

    # its exactly 10 mins long, so we have 0,1,2,3,4,5,6,7,8,9,10 mins.
    assert len(stepper) == 11

    for step in stepper.steps():
        steps.append(step)

    assert len(steps) == 11
    assert steps[0] == timeunits(minutes=0)
    assert steps[1] == timeunits(minutes=1)
    assert steps[10] == timeunits(minutes=10)
