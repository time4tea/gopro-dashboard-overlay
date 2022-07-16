import datetime
import inspect
import os
from array import array
from pathlib import Path
from typing import Tuple

import pytest

from gopro_overlay import ffmpeg
from gopro_overlay.ffmpeg import StreamInfo
from gopro_overlay.gpmd import GoproMeta, GPSFix, GPS5, XYZ, GPMDItem, interpret_item
from gopro_overlay.gpmd_calculate import CorrectionFactorsPacketTimeCalculator, CoriTimestampPacketTimeCalculator
from gopro_overlay.gpmd_visitors import DetermineTimestampOfFirstSHUTVisitor, CalculateCorrectionFactorsVisitor, \
    CorrectionFactors
from gopro_overlay.gpmd_visitors_debug import DebuggingVisitor
from gopro_overlay.gpmd_visitors_gps import GPSVisitor, GPS5EntryConverter, DetermineFirstLockedGPSUVisitor
from gopro_overlay.gpmd_visitors_xyz import XYZVisitor, XYZComponentConverter
from gopro_overlay.point import Point, Point3, Quaternion
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units
from tests.test_framedata import load_file


def path_of_meta(name):
    sourcefile = Path(inspect.getfile(path_of_meta))

    meta_dir = sourcefile.parents[0].joinpath("meta")

    return os.path.join(meta_dir, name)


def load_meta(name):
    with open(path_of_meta(name), "rb") as f:
        arr = array("b")
        arr.frombytes(f.read())
        return arr


def load(name):
    return GoproMeta.parse(load_meta(name))


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
    meta = load("hero5.raw")
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

    meta[0].accept(GPSVisitor(converter=assert_components))


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

    meta[0].accept(GPSVisitor(converter=converter.convert))

    assert counter[0] == 18


def test_load_hero5_raw_accl():
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
            print(f"{g}  = {Point3(g.x, g.y, g.z).length()}")

    meta.accept(GRAVisitor(process_gravities))


def load_mp4_meta(test_file_name, missing_ok=False) -> Tuple[StreamInfo, GoproMeta]:
    filepath = path_of_meta(test_file_name)

    if not os.path.exists(filepath):
        if missing_ok:
            pytest.xfail(f"Missing file {filepath} and this is OK")

    return ffmpeg.find_streams(filepath), load_file(filepath)


# TODO - get time-lapse and time-warp for inclusion

def test_loading_time_lapse_file():
    streams, _ = load_mp4_meta("time-lapse.mp4", missing_ok=True)
    assert streams.audio is None
    assert streams.video == 0
    assert streams.meta.stream == 2
    assert streams.meta.frame_count == 63
    assert streams.meta.frame_duration == 500
    assert streams.meta.timebase == 15000


def test_estimation_of_timestamps_for_timelapse():
    stream_info, meta = load_mp4_meta("time-lapse.mp4", missing_ok=True)
    visitor = meta.accept(CalculateCorrectionFactorsVisitor("GPS5", stream_info.meta))

    factors = visitor.factors()

    assert factors.first_frame == timeunits(seconds=-0.000000)
    assert factors.last_frame == timeunits(seconds=2.100000)
    assert factors.frames_s == pytest.approx(30.000000, 0.0000001)


def test_loading_time_warp_file():
    stream_info, meta = load_mp4_meta("time-warp.mp4", missing_ok=True)
    visitor = meta.accept(CalculateCorrectionFactorsVisitor("GPS5", stream_info.meta))

    factors = visitor.factors()

    assert factors.first_frame == timeunits(seconds=0.000000)
    assert factors.last_frame == timeunits(seconds=2.235566)  # differs by 0.000001 from gpmf-parser frame time
    assert factors.frames_s == pytest.approx(29.970030, 0.0000001)


def test_estimation_of_timestamps():
    ''' use GetGPMFSampleRate on the same file to get the values to assert... '''

    stream_info, meta = load_mp4_meta("hero7.mp4")

    assert stream_info.meta.frame_duration == 1001

    visitor = meta.accept(CalculateCorrectionFactorsVisitor("GPS5", stream_info.meta))

    factors = visitor.factors()

    assert visitor.count == 12
    assert visitor.samples == 219
    assert visitor.meanY == 1427
    assert visitor.meanX == 78.078000000000003

    assert factors.first_frame == timeunits(seconds=-0.0241305)
    assert factors.last_frame == timeunits(seconds=12.002847)
    assert factors.frames_s == pytest.approx(18.209063, 0.0000001)


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
