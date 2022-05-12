import datetime
from datetime import timedelta

import pytest

from gopro_overlay.entry import Entry
from gopro_overlay.gpmd import Point
from gopro_overlay.timeseries import Timeseries
from gopro_overlay.timeseries_process import process_ses, calculate_speeds
from gopro_overlay.units import units, metres


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
    return datetime.datetime.fromtimestamp(i, tz=datetime.timezone.utc)


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


def test_process_delta_speeds():
    ts = Timeseries()
    ts.add(
        Entry(datetime_of(1), point=Point(51.50186, -0.14056)),
        Entry(datetime_of(61), point=Point(51.50665, -0.12895)),
    )
    ts.process_deltas(calculate_speeds())

    entry = ts.get(datetime_of(1))
    assert entry.time == units.Quantity(60, units.s)
    assert "{0.magnitude:.2f} {0.units}".format(entry.dist) == "966.36 meter"
    assert "{0.magnitude:.2f} {0.units:~P}".format(entry.cspeed) == "16.11 m/s"
    assert "{0.magnitude:.2f} {0.units:~P}".format(entry.azi) == "56.53 deg"
    assert "{0.magnitude:.2f} {0.units:~P}".format(entry.cog) == "56.53 deg"


def test_filling_missing_entries():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    dt3 = dt2 + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(Entry(dt1, alt=metres(10)))
    # no entry for dt2
    ts.add(Entry(dt3, alt=metres(30)))

    ts.get(dt1, interpolate=False)
    with pytest.raises(KeyError):
        ts.get(dt2, interpolate=False)

    filled = ts.backfill(timedelta(seconds=1))
    assert filled == 1
    assert ts.get(dt2, interpolate=False).alt.magnitude == 20


def test_filling_missing_entries_2():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=0.9)
    dt3 = dt2 + timedelta(seconds=0.9)
    ts = Timeseries()
    ts.add(Entry(dt1, alt=metres(10)))
    # no entry for dt2
    ts.add(Entry(dt3, alt=metres(30)))

    ts.get(dt1, interpolate=False)

    with pytest.raises(KeyError):
        ts.get(dt2, interpolate=False)

    filled = ts.backfill(timedelta(seconds=1))
    assert filled == 1
    assert ts.get(dt2, interpolate=False).alt.magnitude == 20


def test_no_filling_missing_entries():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=1)
    ts = Timeseries()
    ts.add(Entry(dt1, alt=metres(10)))
    ts.add(Entry(dt2, alt=metres(20)))

    ts.get(dt1, interpolate=False)
    ts.get(dt2, interpolate=False)

    filled = ts.backfill(timedelta(seconds=1))
    assert filled == 0


def test_no_filling_missing_entries_2():
    dt1 = datetime_of(1631178710)
    dt2 = dt1 + timedelta(seconds=0.9)
    ts = Timeseries()
    ts.add(Entry(dt1, alt=metres(10)))
    ts.add(Entry(dt2, alt=metres(19)))

    ts.get(dt1, interpolate=False)
    ts.get(dt2, interpolate=False)

    filled = ts.backfill(timedelta(seconds=1))
    assert filled == 0
