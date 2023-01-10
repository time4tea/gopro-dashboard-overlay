import dataclasses
import math
from typing import Callable, Tuple

import cairo

from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.journey import Journey
from gopro_overlay.point import Point
from gopro_overlay.rdp import rdp
from gopro_overlay.widgets.cairo.cairo import set_source, saved


@dataclasses.dataclass(frozen=True)
class Line:
    fill: Tuple[float, float, float]
    outline: Tuple[float, float, float]
    width: float


black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)

def to_cairo_rgba(pillow_rgba):
    if len(pillow_rgba) == 3:
        return pillow_rgba
    elif len(pillow_rgba) == 4:
        return pillow_rgba[0], pillow_rgba[1], pillow_rgba[2], pillow_rgba[3] / 255.0
    else:
        raise ValueError("Only 3 or 4 tuples, please")

class CairoCircuit:

    def __init__(
            self,
            framemeta: FrameMeta,
            location: Callable[[], Point],
            line: Line = Line(fill=white, outline=black, width=0.01),
            loc: Line = Line(fill=blue, outline=white, width=0.015),
    ):
        self.framemeta = framemeta
        self.location = location

        self.linespec = line
        self.locspec = loc

        self.journey = None
        self.points = None

    def draw(self, context: cairo.Context):
        if self.journey is None:
            self.journey = Journey()
            self.framemeta.process(self.journey.accept)

        bbox = self.journey.bounding_box
        size = bbox.size() * 1.1

        mid_x = ((bbox.max.lat - bbox.min.lat) / 2) + bbox.min.lat
        mid_y = ((bbox.max.lon - bbox.min.lon) / 2) + bbox.min.lon

        def scale(point):
            x = ((point.lat - mid_x) / size.x)
            y = ((point.lon - mid_y) / size.y)
            return x, y

        start = self.journey.locations[0]

        with saved(context):
            context.move_to(*(scale(start)))

            if self.points is None:
                self.points = rdp([scale(p) for p in self.journey.locations[1:]], epsilon=self.linespec.width / 8)

            [context.line_to(*p) for p in self.points]

            set_source(context, to_cairo_rgba(self.linespec.outline))
            context.set_line_width(self.linespec.width)
            context.stroke_preserve()

            set_source(context, to_cairo_rgba(self.linespec.fill))
            context.set_line_width(self.linespec.width * 0.75)
            context.stroke()

            with saved(context):
                context.translate(*(scale(self.location())))
                context.arc(0, 0, self.locspec.width, 0, math.tau)
                set_source(context, to_cairo_rgba(self.locspec.outline))
                context.stroke_preserve()
                set_source(context, to_cairo_rgba(self.locspec.fill))
                context.fill()
