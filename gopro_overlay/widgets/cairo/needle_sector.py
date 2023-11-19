from typing import List, Callable

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.cairo import CairoWidget, saved
from gopro_overlay.widgets.cairo.colour import Colour
from gopro_overlay.widgets.cairo.ellipse import EllipseParameters
from gopro_overlay.widgets.cairo.gauge_marker import circle_with_radius
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.reading import Reading


class SectorNeedle(CairoWidget):

    def __init__(
            self,
            inner: EllipseParameters,
            outer: EllipseParameters,
            lines: List[LineParameters],
            start: Angle,
            length: Angle,
            reading: Callable[[], Reading] = lambda: Reading.full()
    ):
        self.inner = inner
        self.outer = outer
        self.lines = lines
        self.start = start.radians()
        self.length = length.radians()
        self.reading = reading

    def draw(self, context: cairo.Context):
        current = self.length * self.reading().value()

        with saved(context):
            context.new_path()

            point_from = self.inner.get_point(self.inner * (self.start + current))
            point_to = self.outer.get_point(self.outer * (self.start + current))

            context.move_to(*point_from.tuple())
            context.line_to(*point_to.tuple())

            for line in self.lines:
                line.apply_to(context)
                context.stroke_preserve()

            context.new_path()


class SectorArc(CairoWidget):

    def __init__(
            self,
            inner: float,
            outer: float,
            inner_colour: Colour,
            outer_colour: Colour,
            start: Angle,
            length: Angle,
            reading_min: Callable[[], Reading] = lambda: Reading(0),
            reading_max: Callable[[], Reading] = lambda: Reading.full()
    ):
        centre = Coordinate(0, 0)
        self.inner_radius = inner
        self.outer_radius = outer
        self.inner = circle_with_radius(inner, centre)
        self.outer = circle_with_radius(outer, centre)
        self.start = start.radians()
        self.length = length.radians()
        self.inner_colour = inner_colour
        self.outer_colour = outer_colour

        self.gradient = cairo.RadialGradient(0, 0, self.inner_radius, 0, 0, self.outer_radius)
        self.gradient.add_color_stop_rgba(0.0, *self.inner_colour.rgba())
        self.gradient.add_color_stop_rgba(1.0, *self.outer_colour.rgba())

        self.reading_min = reading_min
        self.reading_max = reading_max

    def draw(self, context: cairo.Context):
        current_min = self.length * self.reading_min().value()
        current_max = self.length * self.reading_max().value()

        if current_min > current_max:
            current_max, current_min = current_min, current_max

        with saved(context):
            point_from = self.inner.get_point(self.inner * (self.start + current_min))
            point_to = self.inner.get_point(self.outer * (self.start + current_max))

            context.move_to(*point_from.tuple())
            context.arc(0, 0, self.outer_radius, self.start + current_min, self.start + current_max)
            context.line_to(*point_to.tuple())
            context.arc_negative(0, 0, self.inner_radius, self.start + current_max, self.start + current_min)
            context.set_source(self.gradient)
            context.fill()
