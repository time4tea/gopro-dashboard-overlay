import math
from typing import Callable, List, Optional

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
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


class CairoMarker:
    def draw(self, context: cairo.Context, coordinate: Coordinate):
        raise NotImplementedError()


class MarkerCircle(CairoMarker):

    def __init__(self,
                 outer: LineParameters,
                 inner: LineParameters,
                 ):
        self.outer = outer
        self.inner = inner

    def draw(self, context: cairo.Context, coordinate: Coordinate):
        context.arc(coordinate.x, coordinate.y, 0.05, 0, math.tau)
        self.outer.apply_to(context)
        context.fill()

        context.arc(coordinate.x, coordinate.y, 0.03, 0, math.tau)
        self.inner.apply_to(context)
        context.fill()


class CairoEllipseMarker(CairoWidget):

    def __init__(self,
                 ellipse: EllipseParameters,
                 start: Angle,
                 length: Angle,
                 marker: CairoMarker,
                 reading,
                 ):
        self.ellipse = ellipse
        self.reading = reading
        self.start = start
        self.length = length
        self.marker = marker

    def draw(self, context: cairo.Context):
        to = self.start + (self.length * self.reading().value())
        coordinate = self.ellipse.get_point(to.radians())

        with saved(context):
            context.rotate(self.ellipse.angle)
            self.marker.draw(context, coordinate)


def minimum_reading(m: Reading, r: Callable[[], Reading]) -> Callable[[], Reading]:
    def f():
        v = r()
        return m if v < m else v

    return f


def circle_with_radius(r: float) -> EllipseParameters:
    return EllipseParameters(Coordinate(0.0, 0.0), major_curve=1.0 / r, minor_radius=r, angle=0)


def ifnone(v, d):
    if v is None:
        return d
    return d


class CairoGaugeMarker(CairoWidget):
    def __init__(
            self,
            start=Angle(degrees=90),
            length=Angle(degrees=270),
            sectors=6,
            tick_colour: Colour = Colour(1, 1, 1),
            gauge_colour: Colour = Colour.hex("00BFFF"),
            marker_outer: Optional[Colour] = None,
            marker_inner: Optional[Colour] = None,
            background_colour: Optional[Colour] = None,
            cap: cairo.LineCap = cairo.LINE_CAP_SQUARE,
            reading: Callable[[], Reading] = lambda: Reading.full(),
    ):
        tick_every = length / sectors
        reading = minimum_reading(Reading(0.0001), reading)
        marker_outer = ifnone(marker_outer, tick_colour.alpha(0.7))
        marker_inner = ifnone(marker_inner, gauge_colour.alpha(0.7))
        background_colour = ifnone(background_colour, tick_colour.alpha(0.2))

        gauge_shadow = gauge_colour.darken(0.2)

        marker = MarkerCircle(
            outer=LineParameters(0.05, colour=marker_outer),
            inner=LineParameters(0.05, colour=marker_inner),
        )

        self.widget = CairoComposite([
            CairoSimpleBackground(
                arc=Arc(
                    ellipse=circle_with_radius(0.45),
                    start=start,
                    length=Angle(degrees=360)
                ),
                colour=background_colour
            ),
            CairoScale(
                outer=circle_with_radius(0.45),
                inner=circle_with_radius(0.35),
                tick=TickParameters(tick_every),
                lines=[
                    LineParameters(0.02, tick_colour, cap=cap)
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
                tick=TickParameters(tick_every),
                lines=[
                    LineParameters(0.02, tick_colour, cap=cap),
                    LineParameters(0.018, gauge_shadow, cap=cap)
                ],
                start=start,
                length=length,
                reading=reading,
            ),
            CairoEllipseMarker(
                ellipse=circle_with_radius(0.40),
                start=start,
                length=length,
                marker=marker,
                reading=reading,
            )
        ])

    def draw(self, context: cairo.Context):
        self.widget.draw(context)
