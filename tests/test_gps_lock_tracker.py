from gopro_overlay.counter import ReasonCounter
from gopro_overlay.gpmd import GPSFix
from gopro_overlay.gpmd_filters import GPSLockTracker, GPSLockComponents, GPSDOPFilter, GPSMaxSpeedFilter, GPSReportingFilter
from gopro_overlay.point import Point


# When GPS Lock is acquired part way through a packet, the GPSF will indicate "LOCKED", but actually
# it only becomes locked part way through the packet. Often, the GPS will be emitting duplicate stale values repeatedly
# until the index where it sorts itself out.
def test_gps_lock_tracking_immediately_locked():
    tracker = GPSLockTracker()
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.0, 1.0), 1.0, 99)) == GPSFix.LOCK_3D
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.2, 1.2), 1.1, 99)) == GPSFix.LOCK_3D


def test_gps_lock_tracker_loses_lock():
    tracker = GPSLockTracker()
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.0, 1.0), 8.0, 99)) == GPSFix.LOCK_3D
    assert tracker.submit(GPSLockComponents(GPSFix.NO, Point(1.2, 1.2), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.2, 1.2), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.2, 1.2), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.3, 1.3), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.3, 1.3), 7.6, 99)) == GPSFix.LOCK_3D


def test_gps_lock_tracker_gains_lock():
    tracker = GPSLockTracker()
    assert tracker.submit(GPSLockComponents(GPSFix.NO, Point(1.0, 1.0), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.NO, Point(1.0, 1.0), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.NO, Point(1.0, 1.0), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.1, 1.1), 8.0, 99)) == GPSFix.NO
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.1, 1.1), 4.3, 99)) == GPSFix.LOCK_2D
    assert tracker.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.1, 1.1), 4.3, 99)) == GPSFix.LOCK_3D


def test_dop_filter():
    filter = GPSDOPFilter(10)
    assert filter.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 10)) == GPSFix.LOCK_2D
    assert filter.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 10.1)) == GPSFix.NO
    assert filter.submit(GPSLockComponents(GPSFix.NO, Point(1.0, 1.0), 8.0, 9)) == GPSFix.NO
    assert filter.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.0, 1.0), 8.0, 9)) == GPSFix.LOCK_3D
    assert filter.submit(GPSLockComponents(GPSFix.LOCK_3D, Point(1.0, 1.0), 8.0, 10.1)) == GPSFix.NO


def test_max_speed_filter():
    filter = GPSMaxSpeedFilter(10)

    assert filter.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 10)) == GPSFix.LOCK_2D
    assert filter.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 10.1, 10)) == GPSFix.NO


def test_reporting_filter():
    counter = ReasonCounter()

    filter = GPSReportingFilter(GPSDOPFilter(10), submitted=counter.inc("DOP Submitted"), rejected=counter.inc("DOP Rejected"))
    assert filter.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 10)) == GPSFix.LOCK_2D
    assert filter.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 10.1)) == GPSFix.NO
    assert filter.submit(GPSLockComponents(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0, 10.1)) == GPSFix.NO

    assert counter.get("DOP Rejected") == 2
    assert counter.get("DOP Submitted") == 3
