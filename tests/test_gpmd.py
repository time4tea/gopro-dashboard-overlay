import datetime
import inspect
import os
from array import array
from pathlib import Path
from typing import Tuple

import pytest

from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import GoproRecording, FFMPEGGoPro
from gopro_overlay.gpmf import GPMD, GPSFix, GPS5, XYZ, GPMDItem, interpret_item
from gopro_overlay.gpmd_calculate import CorrectionFactorsPacketTimeCalculator, CoriTimestampPacketTimeCalculator
from gopro_overlay.gpmd_visitors import DetermineTimestampOfFirstSHUTVisitor, CalculateCorrectionFactorsVisitor, \
    CorrectionFactors
from gopro_overlay.gpmd_visitors_debug import DebuggingVisitor
from gopro_overlay.gpmd_visitors_gps import GPS5Visitor, GPS5EntryConverter, DetermineFirstLockedGPSUVisitor
from gopro_overlay.gpmd_visitors_xyz import XYZVisitor, XYZComponentConverter
from gopro_overlay.point import Point, Point3, Quaternion
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units
from tests.test_framedata import load_file


def path_of_meta(name) -> Path:
    sourcefile = Path(inspect.getfile(path_of_meta))

    meta_dir = sourcefile.parents[0].joinpath("meta")

    return meta_dir / name


def load_meta(name):
    with open(path_of_meta(name), "rb") as f:
        arr = array("b")
        arr.frombytes(f.read())
        return arr


def load(name):
    return GPMD.parse(load_meta(name))


def test_load_hero6_raw():
    meta = load("hero6.raw")
    assert len(meta) == 1

    devc = meta[0]
    assert devc.with_type("DVNM")[0].interpret() == "Hero6 Black"
    assert devc.with_type("TICK")[0].interpret() == 342433
    assert devc.fourcc == "DEVC"
    assert devc.itemset == {"DVNM", "DVID", "TICK", "STRM"}
    assert len(devc) == 14


def test_debugging_visitor_at_least_doesnt_blow_up():
    meta = load("hero6.raw")
    meta.accept(DebuggingVisitor())


def test_debugging_visitor_for_mp4():
    _, meta = load_mp4_meta("hero7.mp4")
    meta.accept(DebuggingVisitor())


def test_load_hero5_raw_gps5():
    meta = load("hero5.raw")
    assert len(meta) == 1

    assert meta[0].with_type("DVNM")[0].interpret() == "Camera"

    def assert_components(count, components):
        print(components)
        assert count == 0
        assert components.samples == 18
        assert components.dop == 6.06
        assert components.fix == GPSFix.LOCK_3D
        assert len(components.points) == 18
        assert len(components.points) == components.samples
        assert components.scale == (10000000, 10000000, 1000, 1000, 100)
        assert components.points[0] == GPS5(lat=33.1264969, lon=-117.3273542, alt=-20.184, speed=0.167, speed3d=0.19)

    meta[0].accept(GPS5Visitor(converter=assert_components))


def test_load_hero5_raw_entry():
    meta = load("hero5.raw")
    assert len(meta) == 1

    assert meta[0].with_type("DVNM")[0].interpret() == "Camera"

    counter = [0]

    def assert_item(frame_timestamp, entry):
        counter[0] += 1
        if entry.packet_index.magnitude == 0:
            assert entry.dt == datetime.datetime(2017, 4, 17, 17, 31, 3, tzinfo=datetime.timezone.utc)
            assert entry.dop.magnitude == 6.06
            assert entry.packet.magnitude == 0
            assert entry.packet_index.magnitude == 0
            assert str(entry.point) == str(Point(lat=33.1264969, lon=-117.3273542))  # float comparison
            assert entry.speed == units.Quantity(0.167, units.mps)
            assert entry.alt == units.Quantity(-20.184, units.m)

    converter = GPS5EntryConverter(
        units=units,
        on_item=assert_item,
        calculator=CorrectionFactorsPacketTimeCalculator(CorrectionFactors(
            first_frame=timeunits(seconds=0),
            last_frame=timeunits(seconds=10),
            frames_s=18
        ))
    )

    meta[0].accept(GPS5Visitor(converter=converter.convert))

    assert counter[0] == 18


def test_load_hero6_raw_accl():
    meta = load("hero6.raw")
    assert len(meta) == 1

    def assert_components(count, components):
        print(components)
        assert count == 1
        assert components.samples_total == 806
        assert len(components.points) == 204
        assert components.scale == (418,)
        assert components.points[0] == XYZ(x=9.97846889952153, y=0.05502392344497608, z=3.145933014354067)

    meta[0].accept(XYZVisitor("ACCL", on_item=assert_components))


def test_load_hero6_raw_accl_complete():
    # hero6 - no CORI, so old timestamps, no ORIN, so hardcode orientation?
    meta = load("hero6.raw")

    converter = XYZComponentConverter(
        on_item=lambda t, i: print(f"{t} = {i}"),
        units=units,
        frame_calculator=CorrectionFactorsPacketTimeCalculator(
            CorrectionFactors(timeunits(millis=0), timeunits(millis=50), 50))
    )
    visitor = XYZVisitor("ACCL", on_item=converter.convert)

    meta.accept(visitor)


def test_load_hero6_ble_raw():
    meta = load("hero6+ble.raw")
    assert len(meta) == 2

    assert meta[0].with_type("DVNM")[0].interpret() == "Hero6 Black"
    assert meta[1].with_type("DVNM")[0].interpret() == "SENSORB6"


def test_load_extracted_meta():
    assert len(load("gopro-meta.gpmd")) == 707

    load("gopro-meta.gpmd").accept(DebuggingVisitor())


def test_load_and_visit_extracted_meta():
    meta = load("gopro-meta.gpmd")
    assert len(meta) == 707

    assert meta.accept(CountingVisitor()).count == 108171


def test_load_accel_meta():
    meta = load("accel/rotation-example.gpmd")

    converter = XYZComponentConverter(
        on_item=lambda t, i: print(f"{t} = {i}"),
        units=units,
        frame_calculator=CoriTimestampPacketTimeCalculator(cori_timestamp=timeunits(millis=1))
    )
    visitor = XYZVisitor("ACCL", on_item=converter.convert)

    meta.accept(visitor)


def test_find_first_shut_timestamp():
    meta = load("gopro-meta.gpmd")

    assert meta.accept(DetermineTimestampOfFirstSHUTVisitor()).timestamp == timeunits(micros=3538581891)


# note that this isn't the actual first packet due to firmware bug
def test_find_first_locked_gpsu():
    expected = datetime.datetime(2021, 9, 24, 10, 59, 38, 509000, tzinfo=datetime.timezone.utc)

    assert load("gopro-meta.gpmd").accept(DetermineFirstLockedGPSUVisitor()).packet_time == expected


# noinspection PyPep8Naming
class CORIVisitor:

    def __init__(self, on_item=lambda x: None):
        self._scale = None
        self._on_item = on_item

    def vic_DEVC(self, i, s):
        return self

    def vic_STRM(self, i, s):
        if "CORI" in s:
            return self

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_CORI(self, item):
        self._on_item(item.interpret(self._scale))

    def v_end(self):
        pass


def test_load_rotation_meta():
    meta = load("accel/rotation-example.gpmd")

    def process_quaternions(qlist):
        for q in qlist:
            qq = Quaternion(q.w, Point3(x=q.x, y=q.y, z=q.z))
            print(f"{qq} -> {qq.to_axis_angle()}")

    meta.accept(CORIVisitor(on_item=process_quaternions))


def test_debug_rotation_meta():
    meta = load("accel/rotation-example.gpmd")

    meta.accept(DebuggingVisitor())


class GRAVisitor:

    def __init__(self, on_item=lambda x: None):
        self._scale = None
        self._on_item = on_item

    def vic_DEVC(self, i, s):
        return self

    def vic_STRM(self, i, s):
        if "GRAV" in s:
            return self

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_GRAV(self, item):
        self._on_item(item.interpret(self._scale))

    def v_end(self):
        pass


def test_load_gravity_meta():
    meta = load("accel/rotation-example.gpmd")

    def process_gravities(gravs):
        for g in gravs:
            print(f"{g}  = {Point3(g.a, g.b, g.c).length()}")

    meta.accept(GRAVisitor(process_gravities))


def load_mp4_meta(test_file_name, missing_ok=False) -> Tuple[GoproRecording, GPMD]:
    filepath = path_of_meta(test_file_name)

    if not os.path.exists(filepath):
        if missing_ok:
            pytest.xfail(f"Missing file {filepath} and this is OK")

    g = FFMPEGGoPro(FFMPEG())

    return g.find_recording(filepath), load_file(filepath)


# TODO - get time-lapse and time-warp for inclusion

def test_loading_time_lapse_file():
    streams, _ = load_mp4_meta("time-lapse.mp4", missing_ok=True)
    assert streams.audio is None
    assert streams.video.stream == 0
    assert streams.data.stream == 2
    assert streams.data.frame_count == 63
    assert streams.data.frame_duration == 500
    assert streams.data.timebase == 15000


def test_estimation_of_timestamps_for_timelapse():
    stream_info, meta = load_mp4_meta("time-lapse.mp4", missing_ok=True)
    visitor = meta.accept(CalculateCorrectionFactorsVisitor("GPS5", stream_info.data))

    factors = visitor.factors()

    assert factors.first_frame == timeunits(seconds=-0.000000)
    assert factors.last_frame == timeunits(seconds=2.100000)
    assert factors.frames_s == pytest.approx(30.000000, 0.0000001)


def test_loading_time_warp_file():
    stream_info, meta = load_mp4_meta("time-warp.mp4", missing_ok=True)
    visitor = meta.accept(CalculateCorrectionFactorsVisitor("GPS5", stream_info.data))

    factors = visitor.factors()

    assert factors.first_frame == timeunits(seconds=0.000000)
    assert factors.last_frame == timeunits(seconds=2.235566)  # differs by 0.000001 from gpmf-parser frame time
    assert factors.frames_s == pytest.approx(29.970030, 0.0000001)


class TimestampCalculatingVisitor:

    def __init__(self, shut_timestamp, wanted):
        self.shut_timestamp = shut_timestamp
        self.wanted = wanted
        self.wanted_method_name = f"vi_{self.wanted}"

        self._timestamp = None
        self._samples = None

        self._packet_timestamps = []

        self.calculator = CoriTimestampPacketTimeCalculator(shut_timestamp)

    def vic_DEVC(self, item, contents):
        return self

    def vic_STRM(self, item, contents):
        if self.wanted in contents:
            return self

    def vi_STMP(self, item):
        self._timestamp = item.interpret()

    def vi_TSMP(self, item):
        self._samples = item.interpret()

    def __getattr__(self, name, *args):
        if name == self.wanted_method_name:
            return self._handle_item
        else:
            raise AttributeError(f"{name}")

    def _handle_item(self, item):
        ts = self.calculator.next_packet(self._timestamp, 0, 10)(0)
        self._packet_timestamps.append(ts[0])

    def v_end(self):
        pass


def test_calculation_of_timestamps_gps9():
    ''' use GetGPMFSampleRate on the same file to get the values to assert... '''

    stream_info, meta = load_mp4_meta("/data/richja/gopro/GX010372.MP4", missing_ok=True)

    assert stream_info.data.frame_duration == 1001

    timestamp = meta.accept(DetermineTimestampOfFirstSHUTVisitor()).timestamp

    packet_timestamps = meta.accept(TimestampCalculatingVisitor(timestamp, "GPS9"))._packet_timestamps

    assert packet_timestamps[0] == timeunits(millis=92.745)


def test_estimation_of_timestamps_gps5():
    ''' use GetGPMFSampleRate on the same file to get the values to assert... '''

    stream_info, meta = load_mp4_meta("hero7.mp4")

    assert stream_info.data.frame_duration == 1001

    visitor = meta.accept(CalculateCorrectionFactorsVisitor("GPS5", stream_info.data))

    factors = visitor.factors()

    assert visitor.count == 12
    assert visitor.samples == 219
    assert visitor.meanY == 1427
    assert visitor.meanX == 78.078000000000003

    assert factors.first_frame == timeunits(seconds=-0.0241305)
    assert factors.last_frame == timeunits(seconds=12.002847)
    assert factors.frames_s == pytest.approx(18.209063, 0.0000001)


def test_estimation_of_timestamps_grav():
    ''' use GetGPMFSampleRate on the same file to get the values to assert... '''

    stream_info, meta = load_mp4_meta("time-warp.mp4", missing_ok=True)

    assert stream_info.data.frame_duration == 1001

    visitor = meta.accept(CalculateCorrectionFactorsVisitor("GRAV", stream_info.data))

    factors = visitor.factors()

    print(factors)


def test_correction_factors_calculator():
    calculator = CorrectionFactorsPacketTimeCalculator(
        CorrectionFactors(
            first_frame=timeunits(seconds=1),
            last_frame=timeunits(seconds=10),
            frames_s=20
        )
    )

    assert calculator.next_packet(-1000, 0, 20)(0) == (timeunits(millis=1000), timeunits(millis=0))
    assert calculator.next_packet(-1000, 0, 20)(1) == (timeunits(millis=1050), timeunits(millis=50))
    assert calculator.next_packet(-1000, 0, 20)(19) == (timeunits(millis=1950), timeunits(millis=950))
    assert calculator.next_packet(-1000, 20, 20)(0) == (timeunits(millis=2000), timeunits(millis=0))


class CountingVisitor:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def __getattr__(self, item):
        if item.startswith("vi_"):
            return lambda x: self.inc()
        if item.startswith("vic_"):
            return lambda i, s: self

    def v_end(self):
        pass


def test_interpreting_strings():
    assert interpret_item(GPMDItem("SIUN", 143, 4, 1, 12, bytes([0x6d, 0x2f, 0x73, 0xb2]))) == "m/s²"
