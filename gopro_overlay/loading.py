import dataclasses
import traceback
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Set, Optional

from gopro_overlay import gpx, fit
from gopro_overlay.ffmpeg_gopro import FFMPEGGoPro, GoproRecording
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.framemeta_gpmd import LoadFlag, parse_gopro
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


class GoproLoader:

    def __init__(self,
                 ffmpeg_gopro: FFMPEGGoPro,
                 units,
                 flags: Optional[Set[LoadFlag]] = None,
                 gps_lock_filter: GPSLockFilter = NullGPSLockFilter()):
        self.ffmpeg_gopro = ffmpeg_gopro
        self.units = units
        self.filter = gps_lock_filter
        self.flags = flags if flags is not None else None

    def load(self, file: Path) -> GoPro:
        recording = self.ffmpeg_gopro.find_recording(file)

        if not recording.data:
            raise IOError(f"Unable to locate metadata stream in '{file}' - is it a GoPro file")

        try:
            frame_meta = parse_gopro(
                recording.load_data(),
                self.units,
                recording.data,
                flags=self.flags,
                gps_lock_filter=self.filter
            )

            return GoPro(recording=recording, framemeta=frame_meta)

        except TimeoutExpired:
            traceback.print_exc()
            fatal(
                f"{file} appears to be located on a slow device. Please ensure both input and output files are on "
                f"fast disks")
