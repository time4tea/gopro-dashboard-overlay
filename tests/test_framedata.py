import datetime
import inspect
from pathlib import Path

import pytest

from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.framemeta_gpmd import gps_framemeta, accl_framemeta, grav_framemeta, cori_framemeta, merge_frame_meta
from gopro_overlay.gpmf import GPMD
from gopro_overlay.gpmd_calculate import PacketTimeCalculator
from gopro_overlay.gpmd_visitors_gps import GPS9Visitor, GPS9EntryConverter
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units

g = FFMPEGGoPro(FFMPEG())


def load_file(path: Path) -> GPMD:
    recording = g.find_recording(path)
    return GPMD.parse(recording.load_data())


def file_path_of_test_asset(name, missing_ok=False) -> Path:
    sourcefile = Path(inspect.getfile(file_path_of_test_asset))

    meta_dir = sourcefile.parents[0].joinpath("meta")

    the_path = Path(meta_dir) / name

    if not the_path.exists():
        if missing_ok:
            pytest.xfail(f"Missing file {the_path} and this is OK")
        else:
            raise IOError(f"Test file {the_path} does not exist")

    return the_path


def test_loading_data_by_frame():
    filepath = file_path_of_test_asset("hero7.mp4")
    meta = load_file(filepath)

    metameta = g.find_recording(filepath).data

    gps_framemeta(
        meta,
        datastream=metameta,
        units=units
    )


def test_loading_accl():
    filepath = file_path_of_test_asset("../../render/test-rotating-slowly.MP4", missing_ok=True)
    meta = load_file(filepath)
    stream_info = g.find_recording(filepath)

    framemeta = accl_framemeta(meta, units, stream_info.data)

    item = list(framemeta.items())[0]
    assert f"{item.accl.x.units:P~}" == "m/s²"
    assert f"{item.accl.y.units:P~}" == "m/s²"
    assert f"{item.accl.z.units:P~}" == "m/s²"


def test_loading_grav():
    filepath = file_path_of_test_asset("../../render/test-rotating-slowly.MP4", missing_ok=True)
    meta = load_file(filepath)
    stream_info = g.find_recording(filepath)

    framemeta = grav_framemeta(meta, units, stream_info.data)

    item = list(framemeta.items())[0]
    assert item.grav.x.magnitude == pytest.approx(0.046, 0.01)
    assert item.grav.y.magnitude == pytest.approx(-0.189, 0.01)
    assert item.grav.z.magnitude == pytest.approx(-0.98, 0.01)
    assert item.grav.length().magnitude == pytest.approx(1.0, 0.0001)


def test_loading_cori():
    filepath = file_path_of_test_asset("../../render/test-rotating-slowly.MP4", missing_ok=True)
    meta = load_file(filepath)
    stream_info = g.find_recording(filepath)

    framemeta = cori_framemeta(meta, units, stream_info.data)

    item = list(framemeta.items())[0]
    assert item.cori.w == pytest.approx(1, abs=0.001)
    assert item.cori.v.x == pytest.approx(0.000, abs=0.001)
    assert item.cori.v.y == pytest.approx(0.005, abs=0.001)
    assert item.cori.v.z == pytest.approx(0.002, abs=0.001)


class TestPacketTimeCalculator(PacketTimeCalculator):

    def __init__(self):
        self.counter = 0

    def next_packet(self, timestamp, samples_before_this, num_samples):
        start = timeunits(seconds=self.counter)
        self.counter += 1
        per_sample = timeunits(seconds=1) / num_samples
        return lambda x: (start + (x * per_sample), (x * per_sample))


def test_loading_gps9():
    filepath = file_path_of_test_asset("gps9.gpmd")

    gpmd = GPMD.parse(filepath.read_bytes())

    frame_meta = FrameMeta()
    gpmd.accept(
        GPS9Visitor(
            converter=GPS9EntryConverter(
                units,
                calculator=TestPacketTimeCalculator(),
                on_item=lambda c, e: frame_meta.add(c, e),
            ).convert
        )
    )

    assert len(frame_meta) == 3621
    entry = next(frame_meta.items())
    assert entry.dt == datetime.datetime(2023, 10, 1, 8, 18, 25, 700000, tzinfo=datetime.timezone.utc)


def test_loading_gps_and_accl():
    filepath = file_path_of_test_asset("../../render/test-rotating-slowly.MP4", missing_ok=True)
    meta = load_file(filepath)
    stream_info = g.find_recording(filepath)

    gps_frame_meta = gps_framemeta(meta, units, stream_info.data)
    accl_frame_meta = accl_framemeta(meta, units, stream_info.data)

    merge_frame_meta(gps_frame_meta, accl_frame_meta, lambda a: {"accl": a.accl})

    for item in gps_frame_meta.items():
        assert item.accl
        assert item.point
