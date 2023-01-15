from gopro_overlay.gpmd import GPSFix, GPS_FIXED
from gopro_overlay.gpmd_visitors_gps import GPSLockTracker
from gopro_overlay.point import Point



# When GPS Lock is acquired part way through a packet, the GPSF will indicate "LOCKED", but actually
# it only becomes locked part way through the packet. Often, the GPS will be emitting duplicate stale values repeatedly
# until the index where it sorts itself out.
def test_gps_lock_tracking_immediately_locked():
    tracker = GPSLockTracker()
    assert tracker.submit(GPSFix.LOCK_3D, Point(1.0, 1.0), 1.0) == GPSFix.LOCK_3D
    assert tracker.submit(GPSFix.LOCK_3D, Point(1.2, 1.2), 1.1) == GPSFix.LOCK_3D


def test_gps_lock_tracker_loses_lock():
    tracker = GPSLockTracker()
    assert tracker.submit(GPSFix.LOCK_3D, Point(1.0, 1.0), 8.0) == GPSFix.LOCK_3D
    assert tracker.submit(GPSFix.NO, Point(1.2, 1.2), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_3D, Point(1.2, 1.2), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_3D, Point(1.2, 1.2), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_3D, Point(1.3, 1.3), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_3D, Point(1.3, 1.3), 7.6) == GPSFix.LOCK_3D


def test_gps_lock_tracker_gains_lock():
    tracker = GPSLockTracker()
    assert tracker.submit(GPSFix.NO, Point(1.0, 1.0), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.NO, Point(1.0, 1.0), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.NO, Point(1.0, 1.0), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_2D, Point(1.0, 1.0), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_2D, Point(1.1, 1.1), 8.0) == GPSFix.NO
    assert tracker.submit(GPSFix.LOCK_2D, Point(1.1, 1.1), 4.3) == GPSFix.LOCK_2D
    assert tracker.submit(GPSFix.LOCK_3D, Point(1.1, 1.1), 4.3) == GPSFix.LOCK_3D
