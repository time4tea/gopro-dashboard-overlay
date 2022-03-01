from datetime import timedelta

import progressbar

from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGGenerate
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.gpmd import timeseries_from_data
from gopro_overlay.layout import Overlay
from gopro_overlay.layout_components import moving_journey_map
from gopro_overlay.point import Coordinate
from gopro_overlay.units import units


def scene(timeseries, renderer):
    def create_scene(entry):
        return [moving_journey_map(
            at=Coordinate(0, 0),
            entry=entry,
            size=256,
            renderer=renderer,
            timeseries=timeseries,
            zoom=14
        )]

    return create_scene


if __name__ == "__main__":

    with open("tests/meta/gopro-meta.gpmd", "rb") as f:
        data = f.read()

    timeseries = timeseries_from_data(data=data, units=units)

    dimension = Dimension(256, 256)
    with CachingRenderer().open() as renderer:
        overlay = Overlay(
            dimensions=dimension,
            timeseries=timeseries,
            create_widgets=scene(timeseries, renderer)
        )

        stepper = timeseries.stepper(timedelta(seconds=0.1))

        ffmpeg = FFMPEGGenerate(
            output="render/scratch.mp4",
            overlay_size=dimension
        )

        progress = progressbar.ProgressBar(
            widgets=[
                'Render: ', progressbar.Counter(), ' [', progressbar.Percentage(), '] ', progressbar.Bar(), ' ', progressbar.ETA()
            ],
            poll_interval=2.0,
            max_value=len(stepper)
        )

        with ffmpeg.generate() as writer:
            for index, dt in enumerate(stepper.steps()):
                progress.update(index)
                writer.write(overlay.draw(dt).tobytes())
