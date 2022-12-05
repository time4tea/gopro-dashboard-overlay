import random
from datetime import timedelta
from typing import Callable

import cairo
from PIL import Image, ImageDraw

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from gopro_overlay.exceptions import Defect
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.journey import Journey
from gopro_overlay.point import Point
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.widgets.map import Circuit
from tests.approval import approve_image
from tests.test_widgets import time_rendering

rng = random.Random()
rng.seed(12345)

ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


class CairoCircuit:

    def __init__(self, dimensions: Dimension, framemeta: FrameMeta, location: Callable[[], Point]):
        self.framemeta = framemeta
        self.location = location
        self.dimensions = dimensions
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, dimensions.x, dimensions.y)

        self.drawn = False

    def draw(self, image: Image, draw: ImageDraw):
        if not self.drawn:
            journey = Journey()
            self.framemeta.process(journey.accept)

            bbox = journey.bounding_box
            size = bbox.size() * 1.1

            ctx = cairo.Context(self.surface)
            ctx.scale(self.dimensions.x, self.dimensions.y)

            def scale(point):
                x = (point.lat - bbox.min.lat) / size.x
                y = (point.lon - bbox.min.lon) / size.y
                return x, y

            start = journey.locations[0]
            ctx.move_to(*scale(start))

            [ctx.line_to(*scale(p)) for p in journey.locations[1:]]

            line_width = 0.01

            ctx.set_source_rgb(0.3, 0.2, 0.5)  # Solid color
            ctx.set_line_width(line_width)
            ctx.stroke_preserve()

            ctx.set_source_rgb(1, 1, 1)  # Solid color
            ctx.set_line_width(line_width / 4)
            ctx.stroke()

            self.drawn = True

        image.alpha_composite(to_pillow(self.surface), (0, 0))


def to_pillow(surface: cairo.ImageSurface) -> Image:
    size = (surface.get_width(), surface.get_height())
    stride = surface.get_stride()

    format = surface.get_format()
    if format != cairo.FORMAT_ARGB32:
        raise Defect(f"Only support ARGB32 images, not {format}")

    with surface.get_data() as memory:
        return Image.frombuffer("RGBA", size, memory.tobytes(), 'raw', "BGRa", stride)


@approve_image
def test_circuit():
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            Circuit(
                dimensions=Dimension(500, 500),
                framemeta=ts,
                privacy_zone=NoPrivacyZone(),
                location=lambda: ts.get(ts.min).point,
            )
        ],
        repeat=100
    )
