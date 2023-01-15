import collections
import datetime
from datetime import timedelta

from gopro_overlay import fake
from gopro_overlay.entry import Entry
from gopro_overlay.framemeta import FrameMeta, Window
from gopro_overlay.point import Point
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units
from tests.test_timeseries import datetime_of

TUP = collections.namedtuple("TUP", "time lat lon alt hr cad atemp")


def test_creating_entry_from_namedtuple():
    some_tuple = TUP(time=datetime_of(1631178710), lat=10.0, lon=100.0, alt=-10, hr=100, cad=90,
                     atemp=17)
    entry = Entry(some_tuple.time, **some_tuple._asdict())
    assert entry.lat == 10.0


def test_putting_in_a_point_gets_back_that_point():
    fm = FrameMeta()
    fm.add(timeunits(seconds=1), Entry(datetime_of(0), point=Point(lat=1.0, lon=1.0), alt=12))
    fm.add(timeunits(seconds=2), Entry(datetime_of(1), point=Point(lat=2.0, lon=1.0), alt=12))
    assert fm.get(timeunits(seconds=1)).point.lat == 1.0
    assert fm.get(timeunits(seconds=2)).point.lat == 2.0


def test_iterating_empty():
    fm = FrameMeta()
    assert len(list(fm.items())) == 0
    assert len(fm) == 0
    assert not bool(fm)


def test_size():
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(1), a=1))
    fm.add(timeunits(seconds=1), Entry(datetime_of(2), a=1))
    assert len(fm) == 2
    assert bool(fm)


def test_iterates_in_frame_time_order_not_insertion_order():
    fm = FrameMeta()
    fm.add(timeunits(seconds=2), Entry(datetime_of(2), point=Point(lat=3.0, lon=1.0), alt=12))
    fm.add(timeunits(seconds=1), Entry(datetime_of(1), point=Point(lat=2.0, lon=1.0), alt=12))
    fm.add(timeunits(seconds=0), Entry(datetime_of(0), point=Point(lat=1.0, lon=1.0), alt=12))

    iterator = iter(list(fm.items()))
    assert next(iterator).point.lat == 1.0
    assert next(iterator).point.lat == 2.0
    assert next(iterator).point.lat == 3.0

    assert fm.duration() == timeunits(seconds=2)


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
    assert fm.duration() == timeunits(seconds=1)


def test_getting_intermediate_point_gets_earlier():
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(0), lat=1.0))
    fm.add(timeunits(seconds=1), Entry(datetime_of(1), lat=2.0))
    fm.add(timeunits(seconds=2), Entry(datetime_of(2), lat=3.0))

    assert fm.get(timeunits(seconds=0)).lat == 1.0
    assert fm.get(timeunits(seconds=1)).lat == 2.0
    assert fm.get(timeunits(seconds=2)).lat == 3.0
    assert fm.get(timeunits(seconds=0.0)).lat == 1.0
    assert fm.get(timeunits(seconds=0.1)).lat == 1.0
    assert fm.get(timeunits(seconds=0.2)).lat == 1.0
    assert fm.get(timeunits(seconds=0.3)).lat == 1.0
    assert fm.get(timeunits(seconds=1.0)).lat == 2.0
    assert fm.get(timeunits(seconds=1.1)).lat == 2.0
    assert fm.get(timeunits(seconds=1.2)).lat == 2.0
    assert fm.get(timeunits(seconds=2.0)).lat == 3.0


def test_getting_point_too_far_away():
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(0), lat=1.0))
    fm.add(timeunits(seconds=1), Entry(datetime_of(1), lat=2.0))
    fm.add(timeunits(seconds=10), Entry(datetime_of(2), lat=3.0))

    assert fm.get(timeunits(seconds=20)).dt == datetime_of(2)


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

    window = Window(ts, timeunits(minutes=1), samples=100, key=lambda e: e.bob, missing=0)

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

def test_skipping_items():
    fm = FrameMeta()
    fm.add(timeunits(seconds=0), Entry(datetime_of(0), lat=1.0))
    fm.add(timeunits(seconds=1), Entry(datetime_of(0.5), lat=2.0))
    fm.add(timeunits(seconds=2), Entry(datetime_of(1), lat=3.0))
    fm.add(timeunits(seconds=2.1), Entry(datetime_of(1.5), lat=4.0))
    fm.add(timeunits(seconds=2.2), Entry(datetime_of(1.6), lat=5.0))
    fm.add(timeunits(seconds=2.3), Entry(datetime_of(2.0), lat=6.0))

    skipped = list(fm.items(step=datetime.timedelta(seconds=1)))

    assert len(skipped) == 3
    assert skipped[0].lat == 1.0
    assert skipped[1].lat == 3.0
    assert skipped[2].lat == 6.0