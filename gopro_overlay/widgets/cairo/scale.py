from typing import List, Callable

import cairo

from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.cairo import CairoWidget, saved
from gopro_overlay.widgets.cairo.ellipse import EllipseParameters
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.tick import TickParameters


class CairoScale(CairoWidget):

    def __init__(
            self,
            inner: EllipseParameters,
            outer: EllipseParameters,
            tick: TickParameters,
            lines: List[LineParameters],
            start: Angle,
            length: Angle,
            reading: Callable[[], Reading] = lambda: Reading.full()
    ):
        self.inner = inner
        self.outer = outer
        self.tick = tick
        self.lines = lines
        self.start = start
        self.length = length
        self.reading = reading

    def draw(self, context: cairo.Context):

        current = abs(self.length) * self.reading().value()

        with saved(context):
            context.new_path()

            thick = self.tick.first

            for i in range(0, 1000):
                value = self.tick.step * i

                if value > current:
                    break

                if self.length < Angle.zero():
                    value = -value

                if thick == self.tick.skipped:
                    thick = 1
                else:
                    thick += 1

                    angle_r = (self.start + value).radians()
                    point_from = self.inner.get_point(self.inner * angle_r)
                    point_to = self.outer.get_point(self.outer * angle_r)

                    context.move_to(*point_from.tuple())
                    context.line_to(*point_to.tuple())

            for line in self.lines:
                line.apply_to(context)
                context.stroke_preserve()

            context.new_path()
