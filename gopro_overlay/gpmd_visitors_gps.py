import collections
import datetime

from gopro_overlay.entry import Entry
from gopro_overlay.gpmd import interpret_item, GPS_FIXED, GPS5
from gopro_overlay.point import Point


class GPS5EntryConverter:
    def __init__(self, units, calculator, on_item=lambda c, e: None):
        self._units = units
        self._on_item = on_item
        self._total_samples = 0
        self._frame_calculator = calculator

    def convert(self, counter, components):
        sample_time_calculator = self._frame_calculator.next_packet(
            components.timestamp,
            self._total_samples,
            len(components.points)
        )

        for index, point in enumerate(components.points):
            sample_frame_timestamp, sample_time_offset = sample_time_calculator(index)

            point_datetime = components.basetime + datetime.timedelta(
                microseconds=sample_time_offset.us
            )
            self._on_item(
                sample_frame_timestamp,
                Entry(
                    dt=point_datetime,
                    timestamp=self._units.Quantity(sample_frame_timestamp.millis(), self._units.number),
                    dop=self._units.Quantity(components.dop, self._units.number),
                    packet=self._units.Quantity(counter, self._units.number),
                    packet_index=self._units.Quantity(index, self._units.number),
                    point=Point(point.lat, point.lon),
                    speed=self._units.Quantity(point.speed, self._units.mps),
                    alt=self._units.Quantity(point.alt, self._units.m),
                    gpsfix=components.fix.value
                )
            )
        self._total_samples += len(components.points)

    # noinspection PyPep8Naming


GPS5Components = collections.namedtuple("GPS5Components",
                                        ["samples", "timestamp", "basetime", "fix", "dop", "scale", "points"])


# noinspection PyPep8Naming
class GPS5StreamVisitor:

    def __init__(self, on_end):
        self._on_end = on_end
        self._samples = None
        self._basetime = None
        self._fix = None
        self._scale = None
        self._points = None
        self._timestamp = None
        self._dop = None

    def vi_STMP(self, item):
        self._timestamp = interpret_item(item)

    def vi_TSMP(self, item):
        self._samples = interpret_item(item)

    def vi_GPSU(self, item):
        self._basetime = interpret_item(item)

    def vi_GPSF(self, item):
        self._fix = interpret_item(item)

    def vi_GPSP(self, item):
        self._dop = interpret_item(item)

    def vi_SCAL(self, item):
        self._scale = interpret_item(item)

    def vi_GPS5(self, item):
        self._points = interpret_item(item, self._scale)

    def v_end(self):
        self._on_end(GPS5Components(
            samples=self._samples,
            timestamp=self._timestamp,
            basetime=self._basetime,
            fix=self._fix,
            dop=self._dop,
            scale=self._scale,
            points=self._points
        ))


# noinspection PyPep8Naming
class GPSVisitor:

    def __init__(self, converter):
        self._converter = converter
        self._counter = 0

    def vic_DEVC(self, item, contents):
        return self

    def vic_STRM(self, item, contents):
        if "GPS5" in contents:
            return GPS5StreamVisitor(
                on_end=lambda c: self._converter(self._counter, c)
            )

    def v_end(self):
        self._counter += 1
        pass


# have seen stuff like this: lock acquired, DOP reduced, but still location way wrong.
# 121,17,NO,2022-05-05 10:22:55.276481+00:00,43.7064837,31.3332034,99.99
# 122,0,LOCK_2D,2022-05-05 10:22:55.335000+00:00,43.7063872,31.333535,3.16
# ...
# 123,0,LOCK_2D,2022-05-05 10:22:56.325000+00:00,43.3438812,31.8257702,3.16
# 123,1,LOCK_2D,2022-05-05 10:22:56.380320+00:00,39.7817877,2.7167594,3.16

# noinspection PyPep8Naming
class DetermineFirstLockedGPSUVisitor:
    _count = 0
    _basetime = None
    _fix = None
    _scale = None
    _point = None

    def vic_DEVC(self, i, s):
        if self._basetime is None:
            return self

    def vic_STRM(self, i, s):
        if "GPS5" in s:
            return self

    # Crazy bug where first couple of "FIX" GPS packets are not actually fixed, they gradually become correct..
    def vi_GPSU(self, item):
        if self._fix in GPS_FIXED:
            self._count += 1

            if self._count == 3:
                self._basetime = interpret_item(item)

    def vi_GPSF(self, item):
        self._fix = interpret_item(item)

    def vi_SCAL(self, item):
        self._scale = interpret_item(item)

    def vi_GPS5(self, item):
        if self._basetime is not None:
            self._point = interpret_item(item, self._scale)[0]

    @property
    def packet_time(self) -> datetime.datetime:
        return self._basetime

    @property
    def point(self) -> GPS5:
        return self._point

    def v_end(self):
        pass
