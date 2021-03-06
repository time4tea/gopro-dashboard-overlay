from gopro_overlay.entry import Entry
from gopro_overlay.gpmd import GPSFix
from gopro_overlay.journey import Journey
from gopro_overlay.point import Point
from tests.test_timeseries import datetime_of


def test_calculating_bounding_box():
    j = Journey()

    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.LOCK_3D.value, point=Point(-1, -2)))
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.LOCK_3D.value, point=Point(0, 0)))
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.LOCK_3D.value, point=Point(1, 2)))

    assert j.bounding_box == (Point(-1, -2), Point(1, 2))


def test_calculating_bounding_box_zero_size():
    j = Journey()
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.LOCK_3D.value, point=Point(0, 0)))
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.LOCK_3D.value, point=Point(0.00000001, 0.00000001)))

    assert j.bounding_box == (Point(0, 0), Point(0.0001, 0.0001))


def test_calculating_bounding_box_only_bad_gps_values():
    j = Journey()
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.NO.value, point=Point(-1, -2)))
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.NO.value, point=Point(0, 0)))
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.NO.value, point=Point(1, 2)))

    assert j.bounding_box == (Point(-1, -2), Point(1, 2))


def test_calculating_bounding_box_mix_good_and_bad_gps_values():
    j = Journey()
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.NO.value, point=Point(-10, -20)))
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.LOCK_2D.value, point=Point(0, 0)))
    j.accept(Entry(dt=datetime_of(0), gpsfix=GPSFix.LOCK_2D.value, point=Point(1, 2)))

    assert j.bounding_box == (Point(0, 0), Point(1, 2))
