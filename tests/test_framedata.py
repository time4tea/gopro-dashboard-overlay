from datetime import timedelta

from gopro_overlay import ffmpeg
from gopro_overlay.framemeta import framemeta_from_meta
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.units import units
from tests.test_gpmd import DebuggingVisitor


def load_file(path):
    return GoproMeta.parse(ffmpeg.load_gpmd_from(path))


def test_debug_file():
    meta = load_file("/home/richja/dev/gopro-graphics/render/contrib/GH010278.MP4")

    visitor = DebuggingVisitor()

    meta.accept(visitor)


def test_loading_data_by_frame():
    meta = load_file("/data/richja/gopro/GH010079.MP4")

    frames = framemeta_from_meta(meta, units=units)

    print(frames)

    print(frames.get(4013))
    print(frames.get(4065))
    print(frames.get(4030))

    print(frames.items()[-1])

    stepper = frames.stepper(timedelta(seconds=0.1))
    for step in stepper.steps():
        print(step)
