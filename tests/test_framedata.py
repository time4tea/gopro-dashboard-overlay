import inspect
import os
from pathlib import Path

from gopro_overlay import ffmpeg
from gopro_overlay.framemeta import framemeta_from_meta
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units


def load_file(path):
    return GoproMeta.parse(ffmpeg.load_gpmd_from(path))


def test_file_path(name):
    sourcefile = Path(inspect.getfile(test_file_path))

    meta_dir = sourcefile.parents[0].joinpath("meta")

    return os.path.join(meta_dir, name)


def test_loading_data_by_frame():
    # filepath = "/data/richja/gopro/GH010079.MP4"
    filepath = test_file_path("hero7.mp4")
    meta = load_file(filepath)

    # meta.accept(DebuggingVisitor())

    metameta = ffmpeg.find_streams(filepath).meta

    frames = framemeta_from_meta(
        meta,
        metameta=metameta,
        units=units
    )

    print(frames)

    print(frames.get(timeunits(millis=4013)))
    print(frames.get(timeunits(millis=4065)))
    print(frames.get(timeunits(millis=4030)))

    print(frames.items()[-1])

    stepper = frames.stepper(timeunits(seconds=0.1))
    for step in stepper.steps():
        print(step)
