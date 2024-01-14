import dataclasses
import datetime
from typing import List, Optional

from gopro_overlay.entry import Entry
from gopro_overlay.gpmf.calc import PacketTimeCalculator
from gopro_overlay.gpmd_filters import NullGPSLockFilter, GPSLockComponents
from gopro_overlay.gpmf import GPSFix, GPS5, interpret_item, GPS9, GPS_FIXED
from gopro_overlay.log import log
from gopro_overlay.point import Point
from gopro_overlay.timeunits import Timeunit


@dataclasses.dataclass(frozen=True)
class GPS5Components:
    samples: int
    timestamp: Timeunit
    basetime: datetime.datetime
    fix: GPSFix
    dop: float
    scale: int
    points: List[GPS5]


class GPS5EntryConverter:
    def __init__(self, units, calculator: PacketTimeCalculator, on_item=lambda c, e: None,
                 gps_lock_filter=NullGPSLockFilter()):
        self._units = units
        self._on_item = on_item
        self._total_samples = 0
        self._frame_calculator = calculator
        self._tracker = gps_lock_filter
        self._short_packet_count = 0

    def convert(self, counter, components: GPS5Components):

        # Turns out GPS5 can contain no points. Possibly accompanied by EMPT packet?
        point_count = len(components.points)

        if point_count == 0:
            return

        # There should be 18 points per packet generally..
        if point_count <= 10:
            self._short_packet_count += 1
            if self._short_packet_count % 10 == 0:
                log(f"Have seen {self._short_packet_count} suspicious GPS packets. Last was {point_count}/18. GPS is misbehaving? - See https://github.com/time4tea/gopro-dashboard-overlay/issues/141")


        sample_time_calculator = self._frame_calculator.next_packet(
            components.timestamp,
            self._total_samples,
            point_count
        )

        gpsfix = components.fix

        for index, point in enumerate(components.points):
            sample_frame_timestamp, sample_time_offset = sample_time_calculator(index)

            position = Point(point.lat, point.lon)
            speed = self._units.Quantity(point.speed, self._units.mps)

            calculated_fix = self._tracker.submit(GPSLockComponents(gpsfix, position, speed.magnitude, components.dop))

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
                    packet_count=self._units.Quantity(point_count),
                    packet_index=self._units.Quantity(index, self._units.number),
                    point=position,
                    speed=speed,
                    alt=self._units.Quantity(point.alt, self._units.m),
                    gpsfix=calculated_fix.value,
                    gpslock=self._units.Quantity(calculated_fix.value),
                )
            )
        self._total_samples += point_count


class GPS5StreamVisitor:

    def __init__(self, on_end):
        self._on_end = on_end
        self._samples: Optional[int] = None
        self._basetime: Optional[datetime.datetime] = None
        self._fix: Optional[GPSFix] = None
        self._scale: Optional[int] = None
        self._points: Optional[List[GPS5]] = None
        self._timestamp: Optional[Timeunit] = None
        self._dop: Optional[float] = None

    def vi_STMP(self, item):
        self._timestamp = item.interpret()

    def vi_TSMP(self, item):
        self._samples = item.interpret()

    def vi_GPSU(self, item):
        self._basetime = item.interpret()

    def vi_GPSF(self, item):
        self._fix = item.interpret()

    def vi_GPSP(self, item):
        self._dop = item.interpret()

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_GPS5(self, item):
        self._points = interpret_item(item, scale=self._scale)

    def v_end(self):
        if self._basetime is not None:
            self._on_end(GPS5Components(
                samples=self._samples,
                timestamp=self._timestamp,
                basetime=self._basetime,
                fix=self._fix,
                dop=self._dop,
                scale=self._scale,
                points=self._points
            ))
        else:
            log(f"No GPS Date :- Skipping Record with {len(self._points)} samples")


class GPS5Visitor:

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


@dataclasses.dataclass(frozen=True)
class GPS9Components:
    samples: int
    timestamp: Timeunit
    scale: int
    points: List[GPS9]


gps9_date_base = datetime.datetime.fromisoformat("2000-01-01T00:00:00+00:00")


class GPS9EntryConverter:
    def __init__(self, units, calculator: PacketTimeCalculator, on_item=lambda c, e: None,
                 gps_lock_filter=NullGPSLockFilter()):
        self._units = units
        self._on_item = on_item
        self._total_samples = 0
        self._frame_calculator = calculator
        self._tracker = gps_lock_filter

    def convert(self, counter, components: GPS9Components):

        # Turns out GPS9 can contain no points. Possibly accompanied by EMPT packet?
        if len(components.points) == 0:
            return

        sample_time_calculator = self._frame_calculator.next_packet(
            components.timestamp,
            self._total_samples,
            len(components.points)
        )

        for (index, point) in enumerate(components.points):
            sample_frame_timestamp, _ = sample_time_calculator(index)

            position = Point(point.lat, point.lon)
            speed = self._units.Quantity(point.speed, self._units.mps)

            fix = GPSFix(point.fix)
            calculated_fix = self._tracker.submit(GPSLockComponents(fix, position, speed.magnitude, point.dop))

            point_datetime = gps9_date_base + datetime.timedelta(
                days=point.days,
                seconds=point.secs
            )

            self._on_item(
                sample_frame_timestamp,
                Entry(
                    dt=point_datetime,
                    timestamp=self._units.Quantity(sample_frame_timestamp.millis(), self._units.number),
                    dop=self._units.Quantity(point.dop, self._units.number),
                    packet=self._units.Quantity(counter, self._units.number),
                    packet_index=self._units.Quantity(index, self._units.number),
                    point=position,
                    speed=speed,
                    alt=self._units.Quantity(point.alt, self._units.m),
                    gpsfix=calculated_fix.value,
                    gpslock=self._units.Quantity(calculated_fix.value),
                )
            )
        self._total_samples += len(components.points)


class GPS9StreamVisitor:

    def __init__(self, on_end):
        self._on_end = on_end
        self._samples: Optional[int] = None
        self._scale: Optional[int] = None
        self._points: Optional[List[GPS9]] = None
        self._timestamp: Optional[Timeunit] = None

    def vi_STMP(self, item):
        self._timestamp = item.interpret()

    def vi_TSMP(self, item):
        self._samples = item.interpret()

    def vi_TYPE(self, item):
        self._type = item.interpret()

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_GPS9(self, item):
        self._points = interpret_item(item, scale=self._scale, types=self._type)

    def v_end(self):
        self._on_end(GPS9Components(
            samples=self._samples,
            timestamp=self._timestamp,
            scale=self._scale,
            points=self._points
        ))


class GPS9Visitor:

    def __init__(self, converter):
        self._converter = converter
        self._counter = 0

    def vic_DEVC(self, item, contents):
        return self

    def vic_STRM(self, item, contents):
        if "GPS9" in contents:
            return GPS9StreamVisitor(
                on_end=lambda c: self._converter(self._counter, c)
            )

    def v_end(self):
        self._counter += 1
        pass


class DetermineFirstLockedGPSUVisitor:
    """# have seen stuff like this: lock acquired, DOP reduced, but still location way wrong.
    # 121,17,NO,2022-05-05 10:22:55.276481+00:00,43.7064837,31.3332034,99.99
    # 122,0,LOCK_2D,2022-05-05 10:22:55.335000+00:00,43.7063872,31.333535,3.16
    # ...
    # 123,0,LOCK_2D,2022-05-05 10:22:56.325000+00:00,43.3438812,31.8257702,3.16
    # 123,1,LOCK_2D,2022-05-05 10:22:56.380320+00:00,39.7817877,2.7167594,3.16
    """

    def __init__(self):
        self._count = 0
        self._basetime = None
        self._fix = None
        self._scale = None
        self._point = None

    def vic_DEVC(self, i, s):
        if self._basetime is None:
            return self

    def vic_STRM(self, i, s):
        if "GPS5" in s:
            return self

    # Crazy bug where first couple of "FIX" GPS packets are not actually fixed, they gradually become correct..
    # See GPSLockTracker
    def vi_GPSU(self, item):
        if self._fix in GPS_FIXED:
            self._count += 1

            if self._count == 3:
                self._basetime = item.interpret()

    def vi_GPSF(self, item):
        self._fix = item.interpret()

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_GPS5(self, item):
        if self._basetime is not None:
            self._point = interpret_item(item, scale=self._scale)[0]

    @property
    def packet_time(self) -> datetime.datetime:
        return self._basetime

    @property
    def point(self) -> GPS5:
        return self._point

    def v_end(self):
        pass
