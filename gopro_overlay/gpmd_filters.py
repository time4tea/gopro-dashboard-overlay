import dataclasses
from collections import Counter
from typing import Optional, Callable

from pint import Quantity

from gopro_overlay.gpmf import GPSFix, GPS_FIXED
from gopro_overlay.log import log
from gopro_overlay.point import Point, BoundingBox


@dataclasses.dataclass(frozen=True)
class GPSLockComponents:
    fix: GPSFix
    point: Point
    speed: float
    dop: float


class GPSLockFilter:
    def submit(self, components: GPSLockComponents) -> GPSFix:
        raise NotImplemented


class GPSReportingFilter(GPSLockFilter):

    def __init__(self, delegate: GPSLockFilter, submitted=lambda: None, rejected=lambda: None):
        self.delegate = delegate
        self.rejected = rejected
        self.submitted = submitted

    def submit(self, components: GPSLockComponents) -> GPSFix:
        result = self.delegate.submit(components)
        self.submitted()
        if result != components.fix and result == GPSFix.NO:
            self.rejected()
        return result


class NullGPSLockFilter(GPSLockFilter):
    def submit(self, components: GPSLockComponents) -> GPSFix:
        return components.fix


class WorstOfGPSLockFilter(GPSLockFilter):

    def __init__(self, *filters):
        self.filters = filters

    def submit(self, components: GPSLockComponents):
        for f in self.filters:
            result = f.submit(components)
            if result.value < components.fix.value:
                components = dataclasses.replace(components, fix=result)

        return components.fix


class GPSBBoxFilter(GPSLockFilter):
    def __init__(self, bbox: BoundingBox):
        self.bbox = bbox

    def submit(self, components: GPSLockComponents) -> GPSFix:
        if not self.bbox.contains(components.point):
            return GPSFix.NO
        return components.fix


class GPSDOPFilter(GPSLockFilter):
    def __init__(self, max_dop: float):
        self.max_dop = max_dop

    def submit(self, components: GPSLockComponents):
        if components.dop > self.max_dop:
            return GPSFix.NO
        return components.fix


class GPSMaxSpeedFilter(GPSLockFilter):

    def __init__(self, max_speed_mps: float):
        self.max_speed = max_speed_mps

    def submit(self, components: GPSLockComponents) -> GPSFix:
        if components.speed > self.max_speed:
            return GPSFix.NO
        return components.fix


class GPSLockTracker(GPSLockFilter):

    def __init__(self, max_dop=20):
        self.max_dop = max_dop
        self.last = None

    def _update(self, components: GPSLockComponents):
        self.last = components

    def submit(self, components: GPSLockComponents):
        if self.last is None:
            self._update(components)
            return components.fix

        if components.fix in GPS_FIXED:
            if self.last.fix not in GPS_FIXED:
                if components.point == self.last.point or components.speed == self.last.speed:
                    return self.last.fix

        self._update(components)
        return components.fix


def standard(
        dop_max: float,
        speed_max: Quantity,
        bbox: Optional[BoundingBox] = None,
        report: Callable[[str], None] = lambda x: None
) -> GPSLockFilter:
    if bbox is not None:
        bbox_filter = GPSBBoxFilter(bbox=bbox)
    else:
        bbox_filter = NullGPSLockFilter()

    return WorstOfGPSLockFilter(
        GPSReportingFilter(GPSLockTracker(), rejected=lambda: report("Heuristics")),
        GPSReportingFilter(bbox_filter, rejected=lambda: report("Outside BBox")),
        GPSReportingFilter(GPSDOPFilter(dop_max), rejected=lambda: report(f"DOP > {dop_max}")),
        GPSReportingFilter(GPSMaxSpeedFilter(speed_max.to("mps").m), rejected=lambda: report(f"Speed > {speed_max}"))
    )


def poor_report(counter: Counter):
    if counter.total() > 0:
        log(f"\n\nNOTE: {counter.total()} GoPro GPS readings were mapped to 'NO_LOCK', for the following reasons:")
        [log(f"* {k} -> {v}") for k, v in counter.items()]
        log(f"\n\n")
