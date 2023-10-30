from enum import Enum
from typing import Optional, Callable, Set

from gopro_overlay import timeseries_process
from gopro_overlay.ffmpeg_gopro import DataStream
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.gpmf.calc import timestamp_calculator_for_packet_type
from gopro_overlay.gpmd_filters import GPSLockFilter, NullGPSLockFilter
from gopro_overlay.gpmf.visitors.find import StreamFindingVisitor
from gopro_overlay.gpmf.visitors.cori import CORIComponentConverter, CORIVisitor
from gopro_overlay.gpmf.visitors.gps import GPS5EntryConverter, GPS5Visitor, GPS9EntryConverter, GPS9Visitor
from gopro_overlay.gpmf.visitors.grav import GRAVComponentConverter, GRAVisitor
from gopro_overlay.gpmf.visitors.xyz import XYZComponentConverter, XYZVisitor
from gopro_overlay.gpmf.gpmf import GPMD
from gopro_overlay.log import log
from gopro_overlay.timeunits import timeunits
from gopro_overlay.timing import PoorTimer


def gps_framemeta(gpmd: GPMD,
                  units,
                  datastream: Optional[DataStream] = None,
                  gps_lock_filter: GPSLockFilter = NullGPSLockFilter()) -> FrameMeta:
    frame_meta = FrameMeta()

    if gpmd.accept(StreamFindingVisitor("GPS9")).found():
        log(">> Found GPS9 ")
        gpmd.accept(
            GPS9Visitor(
                converter=GPS9EntryConverter(
                    units,
                    calculator=timestamp_calculator_for_packet_type(gpmd, datastream, "GPS9"),
                    on_item=lambda c, e: frame_meta.add(c, e),
                    gps_lock_filter=gps_lock_filter
                ).convert
            )
        )
    elif gpmd.accept(StreamFindingVisitor("GPS5")).found():
        log(">> Found GPS5 ")
        gpmd.accept(
            GPS5Visitor(
                converter=GPS5EntryConverter(
                    units,
                    calculator=timestamp_calculator_for_packet_type(gpmd, datastream, "GPS5"),
                    on_item=lambda c, e: frame_meta.add(c, e),
                    gps_lock_filter=gps_lock_filter
                ).convert
            )
        )
    else:
        log(">> Can't find any GPS information")

    return frame_meta


def accl_framemeta(gpmd: GPMD, units, datastream: Optional[DataStream] = None):
    framemeta = FrameMeta()

    gpmd.accept(
        XYZVisitor(
            "ACCL",
            on_item=XYZComponentConverter(
                frame_calculator=timestamp_calculator_for_packet_type(gpmd, datastream, "ACCL"),
                units=units,
                on_item=lambda t, x: framemeta.add(t, x)
            ).convert
        )
    )

    kalman = timeseries_process.process_kalman_pp3("accl", lambda i: i.accl)
    framemeta.process(kalman)

    return framemeta


def grav_framemeta(gpmd: GPMD, units, datastream: Optional[DataStream] = None):
    framemeta = FrameMeta()

    gpmd.accept(
        GRAVisitor(
            on_item=GRAVComponentConverter(
                frame_calculator=timestamp_calculator_for_packet_type(gpmd, datastream, "GRAV"),
                units=units,
                on_item=lambda t, x: framemeta.add(t, x)
            ).convert
        )
    )

    return framemeta


def cori_framemeta(gpmd: GPMD, units, datastream: Optional[DataStream] = None):
    framemeta = FrameMeta()

    gpmd.accept(
        CORIVisitor(
            on_item=CORIComponentConverter(
                frame_calculator=timestamp_calculator_for_packet_type(gpmd, datastream, "CORI"),
                units=units,
                on_item=lambda t, x: framemeta.add(t, x)
            ).convert
        )
    )

    return framemeta


def merge_frame_meta(gps: FrameMeta, other: FrameMeta, update: Callable[[FrameMeta], dict]):
    if other:
        for item in gps.items():
            frame_time = item.timestamp
            closest_previous = other.get(timeunits(millis=frame_time.magnitude))
            item.update(**update(closest_previous))


class LoadFlag(Enum):
    ACCL = 1
    GRAV = 2
    CORI = 3


def parse_gopro(gpmd_from, units, datastream: DataStream, flags: Set[LoadFlag] = None,
                gps_lock_filter: GPSLockFilter = NullGPSLockFilter()) -> FrameMeta:
    if flags is None:
        flags = set(list(LoadFlag))

    with PoorTimer("parsing").timing():
        with PoorTimer("GPMD", indent=1).timing():
            gpmd = GPMD.parse(gpmd_from)

        with PoorTimer("extract GPS", indent=1).timing():
            gps_frame_meta = gps_framemeta(gpmd, units, datastream=datastream, gps_lock_filter=gps_lock_filter)

        if LoadFlag.ACCL in flags:
            with PoorTimer("extract ACCL", indent=1).timing():
                merge_frame_meta(
                    gps_frame_meta,
                    accl_framemeta(gpmd, units, datastream=datastream),
                    lambda a: {"accl": a.accl}
                )

        if LoadFlag.GRAV in flags:
            with PoorTimer("extract GRAV", indent=1).timing():
                merge_frame_meta(
                    gps_frame_meta,
                    grav_framemeta(gpmd, units, datastream=datastream),
                    lambda a: {"grav": a.grav}
                )

        if LoadFlag.CORI in flags:
            with PoorTimer("extract CORI", indent=1).timing():
                merge_frame_meta(
                    gps_frame_meta,
                    cori_framemeta(gpmd, units, datastream=datastream),
                    lambda a: {"cori": a.cori, "ori": a.ori}
                )

        return gps_frame_meta


def framemeta_from_datafile(datapath, units, datastream: DataStream, flags: Set[LoadFlag] = None):
    with open(datapath, "rb") as data:
        return parse_gopro(data.read(), units, datastream, flags)
