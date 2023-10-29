import dataclasses
import math
from typing import Callable, Tuple

import cairo

from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.journey import Journey
from gopro_overlay.point import Point, Coordinate
from gopro_overlay.rdp import rdp
from gopro_overlay.widgets.cairo.cairo import set_source, saved, CairoWidget, CairoCache, CairoComposite


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


class CairoCircuitPath(CairoWidget):

    def __init__(
            self,
            journey_fn: Callable[[], Journey],
            scale_fn: Callable[[Point], Tuple[float, float]],
            line: Line = Line(fill=white, outline=black, width=0.01),
    ):
        self.journey = journey_fn
        self.scale = scale_fn
        self.line = line

        self._points = None

    def draw(self, context: cairo.Context):
        journey = self.journey()

        with saved(context):
            start = journey.locations[0]
            context.move_to(*(self.scale(start)))

            if self._points is None:
                self._points = rdp([self.scale(p) for p in journey.locations[1:]], epsilon=self.line.width / 8)

            [context.line_to(*p) for p in self._points]

            set_source(context, to_cairo_rgba(self.line.outline))
            context.set_line_width(self.line.width)
            context.stroke_preserve()

            set_source(context, to_cairo_rgba(self.line.fill))
            context.set_line_width(self.line.width * 0.75)
            context.stroke()


class CairoCircuitLocation(CairoWidget):
    def __init__(
            self,
            location_fn: Callable[[], Point],
            scale_fn: Callable[[Point], Tuple[float, float]],
            loc: Line = Line(fill=white, outline=black, width=0.01),
    ):
        self.location = location_fn
        self.scale = scale_fn
        self.loc = loc

    def draw(self, context: cairo.Context):
        with saved(context):
            context.set_line_width(self.loc.width)
            context.translate(*(self.scale(self.location())))
            context.arc(0, 0, self.loc.width, 0, math.tau)
            set_source(context, to_cairo_rgba(self.loc.outline))
            context.stroke_preserve()
            set_source(context, to_cairo_rgba(self.loc.fill))
            context.fill()


class CairoCircuit(CairoWidget):

    def __init__(
            self,
            framemeta: FrameMeta,
            location: Callable[[], Point],
            line: Line = Line(fill=white, outline=black, width=0.01),
            loc: Line = Line(fill=blue, outline=white, width=0.015),
    ):
        self.framemeta = framemeta
        self._journey = None
        self._size = None
        self._mid = None

        self.widget = CairoComposite([
            CairoCache(
                CairoCircuitPath(
                    self.journey,
                    self.scale,
                    line
                )
            ),
            CairoCircuitLocation(
                location,
                self.scale,
                loc,
            )
        ])

    def journey(self):
        if self._journey is None:
            self._journey = Journey()
            self.framemeta.process(self._journey.accept)
            bbox = self._journey.bounding_box
            size = bbox.size() * 1.1

            self._size = max(size.x, size.y)

            self._mid = Coordinate(
                x=((bbox.max.lat - bbox.min.lat) / 2) + bbox.min.lat,
                y=((bbox.max.lon - bbox.min.lon) / 2) + bbox.min.lon
            )
        return self._journey

    def scale(self, point):
        x = ((point.lat - self._mid.x) / self._size)
        y = ((point.lon - self._mid.y) / self._size)
        return x, y

    def draw(self, context: cairo.Context):
        self.widget.draw(context)
