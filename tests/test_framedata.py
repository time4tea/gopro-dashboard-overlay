import inspect
import os
from pathlib import Path

import pytest

from gopro_overlay import ffmpeg
from gopro_overlay.framemeta import gps_framemeta, accl_framemeta, merge_frame_meta
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.units import units


def load_file(path) -> GoproMeta:
    return GoproMeta.parse(ffmpeg.load_gpmd_from(path))


def file_path_of_test_asset(name, missing_ok=False):
    sourcefile = Path(inspect.getfile(file_path_of_test_asset))

    meta_dir = sourcefile.parents[0].joinpath("meta")

    the_path = os.path.join(meta_dir, name)

    if not os.path.exists(the_path):
        if missing_ok:
            pytest.xfail(f"Missing file {the_path} and this is OK")
        else:
            raise IOError(f"Test file {the_path} does not exist")

    return the_path


def test_loading_data_by_frame():
    filepath = file_path_of_test_asset("hero7.mp4")
    meta = load_file(filepath)

    metameta = ffmpeg.find_streams(filepath).meta

    gps_framemeta(
        meta,
        metameta=metameta,
        units=units
    )


def test_loading_accl():
    filepath = file_path_of_test_asset("../../render/test-rotating-slowly.MP4", missing_ok=True)
    meta = load_file(filepath)
    stream_info = ffmpeg.find_streams(filepath)

    framemeta = accl_framemeta(meta, units, stream_info.meta)

    item = framemeta.items()[0]
    assert f"{item.accl.x.units:P~}" == "m/s²"
    assert f"{item.accl.y.units:P~}" == "m/s²"
    assert f"{item.accl.z.units:P~}" == "m/s²"


def test_loading_gps_and_accl():
    filepath = file_path_of_test_asset("../../render/test-rotating-slowly.MP4", missing_ok=True)
    meta = load_file(filepath)
    stream_info = ffmpeg.find_streams(filepath)

    gps_frame_meta = gps_framemeta(meta, units, stream_info.meta)
    accl_frame_meta = accl_framemeta(meta, units, stream_info.meta)

    merge_frame_meta(gps_frame_meta, accl_frame_meta, lambda a: {"accl": a.accl})

    for item in gps_frame_meta.items():
        assert item.accl
        assert item.point
