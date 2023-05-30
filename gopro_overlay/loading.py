import dataclasses
import traceback
from pathlib import Path
from subprocess import TimeoutExpired

from gopro_overlay import gpx, fit
from gopro_overlay.ffmpeg import StreamInfo, find_streams
from gopro_overlay.framemeta import framemeta_from, FrameMeta
from gopro_overlay.gpmd_filters import GPSLockFilter
from gopro_overlay.log import fatal
from gopro_overlay.timeseries import Timeseries


def load_external(filepath: Path, units) -> Timeseries:
    suffix = filepath.suffix.lower()
    if suffix == ".gpx":
        return gpx.load_timeseries(filepath, units)
    elif suffix == ".fit":
        return fit.load_timeseries(filepath, units)
    else:
        fatal(f"Don't recognise filetype from {filepath} - support .gpx and .fit")




@dataclasses.dataclass
class GoPro:
    streams: StreamInfo
    framemeta: FrameMeta


def load_gopro(file: Path, units, filter: GPSLockFilter) -> GoPro:
    stream_info = find_streams(file)

    if not stream_info.meta:
        raise IOError(f"Unable to locate metadata stream in '{file}' - is it a GoPro file")

    try:
        frame_meta = framemeta_from(
            file,
            metameta=stream_info.meta,
            units=units,
            gps_lock_filter=filter
        )

        return GoPro(streams=stream_info, framemeta=frame_meta)

    except TimeoutExpired:
        traceback.print_exc()
        fatal(f"{file} appears to be located on a slow device. Please ensure both input and output files are on fast disks")
