import dataclasses
import traceback
from pathlib import Path
from subprocess import TimeoutExpired

from gopro_overlay import gpx, fit
from gopro_overlay.ffmpeg import GoproRecording, find_recording
from gopro_overlay.framemeta import FrameMeta, parse_gopro
from gopro_overlay.gpmd_filters import GPSLockFilter, NullGPSLockFilter
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
    recording: GoproRecording
    framemeta: FrameMeta


def load_gopro(file: Path, units, filter: GPSLockFilter = NullGPSLockFilter()) -> GoPro:
    recording = find_recording(file)

    if not recording.meta:
        raise IOError(f"Unable to locate metadata stream in '{file}' - is it a GoPro file")

    try:
        frame_meta = parse_gopro(
            recording.load_gpmd(),
            units,
            recording.meta,
            gps_lock_filter=filter
        )

        return GoPro(recording=recording, framemeta=frame_meta)

    except TimeoutExpired:
        traceback.print_exc()
        fatal(f"{file} appears to be located on a slow device. Please ensure both input and output files are on fast disks")


class GoproLoader:

    def __init__(self, units, gps_lock_filter: GPSLockFilter = NullGPSLockFilter()):
        self.units = units
        self.filter = gps_lock_filter

    def load(self, file: Path) -> GoPro:
        return load_gopro(file, self.units, self.filter)
