from datetime import timedelta

from gopro_overlay.entry import Entry
from tests.test_timeseries import datetime_of, metres


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


def test_interpolating_quantity():
    e1 = Entry(datetime_of(0), alt=metres(10))
    e2 = Entry(datetime_of(10), alt=metres(20))

    assert e1.interpolate(e2, datetime_of(1)).alt == metres(11)
