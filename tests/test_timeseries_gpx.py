from datetime import timedelta

from gopro_overlay.point import Point
from gopro_overlay.timeseries import Timeseries, Entry
from gopro_overlay.timeseries_gpx import timeseries_to_gpx
from gopro_overlay.units import metres
from tests.test_timeseries import datetime_of


def test_converting_timeseries_to_gpx():
    dt1 = datetime_of(0)
    dt2 = dt1 + timedelta(seconds=1)
    dt3 = dt1 + timedelta(seconds=2)
    ts = Timeseries()
    ts.add(Entry(dt1, point=Point(lat=1.0, lon=1.0), alt=metres(12)))
    ts.add(Entry(dt2, point=Point(lat=2.0, lon=2.0), alt=metres(11)))
    ts.add(Entry(dt3, point=Point(lat=3.0, lon=3.0), alt=metres(10)))

    gpx = timeseries_to_gpx(ts)

    assert len(gpx.tracks[0].segments[0].points) == 3
    assert gpx.tracks[0].segments[0].points[0].latitude == 1.0
    assert gpx.tracks[0].segments[0].points[0].longitude == 1.0
    assert gpx.tracks[0].segments[0].points[0].elevation == 12.0

    assert gpx.tracks[0].segments[0].points[2].latitude == 3.0
    assert gpx.tracks[0].segments[0].points[2].longitude == 3.0
    assert gpx.tracks[0].segments[0].points[2].elevation == 10.0

