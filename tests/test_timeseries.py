import datetime

from gopro_overlay.entry import Entry
from gopro_overlay.point import Point
from gopro_overlay.timeseries import Timeseries
from gopro_overlay.timeseries_process import process_ses, calculate_speeds
from gopro_overlay.units import units


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
