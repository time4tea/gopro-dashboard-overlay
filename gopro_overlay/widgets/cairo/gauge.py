import math
from typing import Callable, List

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.cairo import CairoWidget, CairoComposite, saved
from gopro_overlay.widgets.cairo.colour import Colour
from gopro_overlay.widgets.cairo.ellipse import EllipseParameters, Arc
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.scale import CairoScale
from gopro_overlay.widgets.cairo.tick import TickParameters


class CairoSimpleBackground(CairoWidget):
    def __init__(self, arc: Arc, colour: Colour):
        self.arc = arc
        self.colour = colour

    def draw(self, context: cairo.Context):
        self.arc.draw(context)
        self.colour.apply_to(context)
        context.fill()


class CairoSimpleGauge(CairoWidget):

    def __init__(self, arc: Arc, lines: List[LineParameters]):
        self.arc = arc
        self.lines = lines

    def draw(self, context: cairo.Context):
        self.arc.draw(context)
        for line in self.lines:
            line.apply_to(context)
            context.stroke_preserve()
        context.new_path()



class CairoEllipseMarker(CairoWidget):

    def __init__(self,
                 ellipse: EllipseParameters,
                 outer: LineParameters,
                 inner: LineParameters,
                 start,
                 length,
                 reading,
                 ):
        self.ellipse = ellipse
        self.outer = outer
        self.inner = inner
        self.reading = reading
        self.start = start
        self.length = length

    def draw(self, context: cairo.Context):
        to = self.start + (self.length * self.reading().value())

        coordinate = self.ellipse.get_point(to)

        with saved(context):
            context.rotate(self.ellipse.angle)

            context.arc(coordinate.x, coordinate.y, 0.05, 0, math.tau)
            self.outer.apply_to(context)
            context.fill()

            context.arc(coordinate.x, coordinate.y, 0.03, 0, math.tau)
            self.inner.apply_to(context)
            context.fill()



def minimum_reading(m: Reading, r: Callable[[], Reading]) -> Callable[[], Reading]:
    def f():
        v = r()
        return m if v < m else v

    return f


def circle_with_radius(r: float) -> EllipseParameters:
    return EllipseParameters(Coordinate(0.0, 0.0), major_curve=1.0 / r, minor_radius=r, angle=0)


class CairoGauge270(CairoWidget):
    def __init__(self, reading: Callable[[], Reading]):
        start = math.pi / 2
        length = math.pi * 3 / 2
        reading = minimum_reading(Reading(0.0001), reading)

        scale_colour = Colour(1, 1, 1)
        gauge_colour = Colour.hex("00BFFF")
        cap = cairo.LINE_CAP_SQUARE

        gauge_shadow = gauge_colour.darken(0.2)

        self.widget = CairoComposite([
            CairoSimpleBackground(
                arc=Arc(
                    ellipse=circle_with_radius(0.45),
                    start=start,
                    length=math.tau
                ),
                colour=scale_colour.alpha(0.2)
            ),
            CairoScale(
                outer=circle_with_radius(0.45),
                inner=circle_with_radius(0.35),
                tick=TickParameters(math.radians(45)),
                lines=[
                    LineParameters(0.02, scale_colour, cap=cap)
                ],
                start=start,
                length=length
            ),
            CairoSimpleGauge(
                arc=Arc(
                    ellipse=circle_with_radius(0.40),
                    start=start,
                    length=length,
                    reading=reading,
                ),
                lines=[
                    LineParameters(0.05, gauge_shadow, cap=cap),
                    LineParameters(0.04, gauge_colour, cap=cap),
                ]
            ),
            CairoScale(
                outer=circle_with_radius(0.41),
                inner=circle_with_radius(0.39),
                tick=TickParameters(math.radians(45)),
                lines=[
                    LineParameters(0.02, scale_colour, cap=cap),
                    LineParameters(0.018, gauge_shadow, cap=cap)
                ],
                start=start,
                length=length,
                reading=reading,
            ),
            CairoEllipseMarker(
                ellipse=circle_with_radius(0.40),
                outer=LineParameters(0.05, colour=scale_colour.alpha(0.7)),
                inner=LineParameters(0.05, colour=gauge_colour.alpha(0.7)),
                start=start,
                length=length,
                reading=reading
            )
        ])

    def draw(self, context: cairo.Context):
        self.widget.draw(context)
