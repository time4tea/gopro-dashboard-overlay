import colorsys
import contextlib
import dataclasses
import functools
import math
from typing import Callable, Tuple, List

import cairo
import pytest

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.cairo import CairoWidget, saved, CairoComposite
from tests import test_widgets_setup
from tests.approval import approve_image
from tests.test_widgets_circuit import cairo_widget_test

ts = test_widgets_setup.ts


@functools.total_ordering
@dataclasses.dataclass
class Reading:
    v: float

    def value(self):
        return max(0.0, min(1.0, self.v))

    @staticmethod
    def full():
        return Reading(1.0)

    def __eq__(self, other):
        if not type(other) == Reading:
            return NotImplemented
        return self.v == other.v

    def __lt__(self, other):
        if not type(other) == Reading:
            return NotImplemented
        return self.v < other.v


def pt():
    return ts.get(ts.min).point


@dataclasses.dataclass(frozen=True)
class HLSColour:
    h: float
    l: float
    s: float
    a: float

    def lighten(self, by: float) -> 'HLSColour':
        return HLSColour(self.h, min(self.l + by, 1.0), self.s, self.a)

    def darken(self, by: float) -> 'HLSColour':
        return HLSColour(self.h, max(self.l - by, 0.0), self.s, self.a)

    def rgb(self) -> 'Colour':
        r, g, b = colorsys.hls_to_rgb(self.h, self.l, self.s)
        return Colour(r, g, b, self.a)


@dataclasses.dataclass(frozen=True)
class Colour:
    r: float
    g: float
    b: float
    a: float = 1.0

    def rgba(self) -> Tuple[float, float, float, float]:
        return self.r, self.g, self.b, self.a

    def rgb(self) -> Tuple[float, float, float]:
        return self.r, self.g, self.b

    def hls(self) -> HLSColour:
        h, l, s = colorsys.rgb_to_hls(self.r, self.g, self.b)
        return HLSColour(h, l, s, self.a)

    def darken(self, by: float) -> 'Colour':
        return self.hls().darken(by).rgb()

    def lighten(self, by: float) -> 'Colour':
        return self.hls().lighten(by).rgb()

    def alpha(self, new_alpha: float):
        return Colour(self.r, self.g, self.b, new_alpha)

    @staticmethod
    def hex(hexcolour: str, alpha=1.0):
        r, g, b = map(lambda v: v / 256.0, tuple(int(hexcolour[i:i + 2], 16) for i in (0, 2, 4)))
        return Colour(r, g, b, alpha)


@dataclasses.dataclass(frozen=True)
class EllipseParameters:
    centre: Coordinate
    major_curve: float = 0.0
    minor_radius: float = 0.0
    angle: float = 0.0

    def __mul__(self, angle) -> float:
        if type(angle) == float:
            if tiny(self.major_curve):
                return angle - self.angle
            else:
                cos_ellipse = math.cos(self.angle)
                sin_ellipse = math.sin(self.angle)
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                return math.atan2(
                    (sin_ellipse * cos_angle + cos_ellipse * sin_angle),
                    (self.major_curve * self.minor_radius * (cos_ellipse * cos_angle - sin_ellipse * sin_angle))
                )
        raise NotImplementedError("only float")

    def cos_gamma(self, angle):
        beta = self.angle + angle
        cos_gamma = math.cos(math.pi / 2.0 + self.angle - beta)

        if tiny(cos_gamma):
            raise ValueError("Infinite coordinate")

        return beta, cos_gamma

    def get_x(self, angle: float) -> float:
        if tiny(self.major_curve):
            beta, cos_gamma = self.cos_gamma(angle)
            return self.centre.x + self.minor_radius * math.cos(beta) / cos_gamma
        else:
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)

            return self.centre.x + cos_angle * math.cos(self.angle) / self.major_curve - sin_angle * math.sin(
                self.angle) * self.minor_radius

    def get_y(self, angle) -> float:
        if tiny(angle):
            beta, cos_gamma = self.cos_gamma(angle)
            return self.centre.y + self.minor_radius * math.sin(beta) / cos_gamma
        else:
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)

            return self.centre.y + cos_angle * math.sin(self.angle) / self.major_curve + sin_angle * math.cos(
                self.angle) * self.minor_radius

    def get(self, angle) -> Coordinate:
        return Coordinate(x=self.get_x(angle), y=self.get_y(angle))

    def get_point(self, angle):
        return self.centre + self.get_relative_point(angle)

    def get_relative_point(self, angle) -> Coordinate:
        if tiny(self.major_curve):
            beta, cos_gamma = self.cos_gamma(angle)

            return Coordinate(
                x=self.minor_radius * math.cos(beta) / cos_gamma,
                y=self.minor_radius * math.sin(beta) / cos_gamma
            )

        else:
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            cos_ellipse = math.cos(self.angle)
            sin_ellipse = math.sin(self.angle)

            return Coordinate(
                x=cos_angle * cos_ellipse / self.major_curve - sin_angle * sin_ellipse * self.minor_radius,
                y=cos_angle * sin_ellipse / self.major_curve + sin_angle * cos_ellipse * self.minor_radius
            )


def tiny(f: float) -> bool:
    return abs(f) < 0.000001


class Arc:
    def __init__(self, ellipse: EllipseParameters, start: float = 0.0, length=2 * math.pi, reading: Callable[[], Reading] = lambda: Reading.full()):
        self.ellipse = ellipse
        self.start = start
        self.length = length
        self.position = reading

    def draw(self, context: cairo.Context):
        to = self.start + (self.length * self.position().value())
        angle = self.ellipse * to - self.start

        if self.length > 0.0:
            if angle < 0.0:
                angle += math.tau
        elif self.length < 0.0:
            if angle > 0.0:
                angle -= math.tau

        if tiny(self.ellipse.major_curve):
            if abs(self.length > math.pi):
                raise ValueError("Constraint")

            context.line_to(*self.ellipse.get(self.start).tuple())
            context.line_to(*self.ellipse.get(to).tuple())
        else:
            with saved(context):
                context.translate(*self.ellipse.centre.tuple())
                context.rotate(self.ellipse.angle)
                context.scale(1.0 / self.ellipse.major_curve, self.ellipse.minor_radius)
                if self.length > 0.0:
                    context.arc(0.0, 0.0, 1.0, self.start, to)
                else:
                    context.arc_negative(0.0, 0.0, 1.0, self.start, to)


cos45 = math.sqrt(2.0) * 0.5


class Gradient:

    @contextlib.contextmanager
    def applied_to(self, context: cairo.Context):
        pattern = cairo.LinearGradient(-cos45, -cos45, cos45, cos45)
        pattern.add_color_stop_rgba(0.0, *Colour(255, 0, 0).rgba())
        pattern.add_color_stop_rgba(1.0, *Colour(0, 255, 0).rgba())
        context.set_source(pattern)
        yield


@dataclasses.dataclass(frozen=True)
class LineParameters:
    width: float
    colour: Colour = Colour(1.0, 1.0, 1.0)
    cap: cairo.LineCap = cairo.LINE_CAP_SQUARE

    def apply_to(self, context: cairo.Context):
        context.set_source_rgba(*self.colour.rgba())
        context.set_line_cap(self.cap)
        context.set_line_width(self.width)


@dataclasses.dataclass(frozen=True)
class TickParameters:
    step: float
    first: int = 0
    skipped: int = -1


class CairoScale(CairoWidget):

    def __init__(
            self,
            inner: EllipseParameters,
            outer: EllipseParameters,
            tick: TickParameters,
            lines: List[LineParameters],
            start: float,
            length: float,
            reading: Callable[[], Reading] = lambda: Reading.full()
    ):
        self.inner = inner
        self.outer = outer
        self.tick = tick
        self.lines = lines
        self.start = start
        self.length = length + tick.step * 0.05
        self.reading = reading

    def draw(self, context: cairo.Context):

        current = self.length * self.reading().value()

        with saved(context):
            context.new_path()

            thick = self.tick.first

            for i in range(0, 1000):
                value = self.tick.step * i
                if value >= current:
                    break

                if thick == self.tick.skipped:
                    thick = 1
                else:
                    thick += 1

                    point_from = self.inner.get_point(self.inner * (self.start + value))
                    point_to = self.outer.get_point(self.outer * (self.start + value))

                    context.move_to(*point_from.tuple())
                    context.line_to(*point_to.tuple())

            for line in self.lines:
                line.apply_to(context)
                context.stroke_preserve()

            context.new_path()


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


def minimum_reading(m: Reading, r: Callable[[], Reading]) -> Callable[[], Reading]:
    def f():
        v = r()
        return m if v < m else v
    return f

def circle_with_radius(r:float) -> EllipseParameters:
    return EllipseParameters(Coordinate(0.0, 0.0), major_curve=1.0 / r, minor_radius=r, angle=0)

class CairoGauge270(CairoWidget):
    def __init__(self, reading: Callable[[], Reading]):
        start = math.pi / 2
        length = math.pi * 3 / 2
        reading = minimum_reading(Reading(0.0001), reading)

        scale_colour = Colour(1,1,1)
        gauge_colour = Colour.hex("2f9bed")

        gauge_shadow = gauge_colour.darken(0.2)

        self.widget = CairoComposite([
            CairoScale(
                outer=circle_with_radius(0.45),
                inner=circle_with_radius(0.35),
                tick=TickParameters(math.radians(45)),
                lines=[
                    LineParameters(0.02, scale_colour, cap=cairo.LINE_CAP_SQUARE)
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
                    LineParameters(0.05, gauge_shadow),
                    LineParameters(0.04, gauge_colour),
                ]
            ),
            CairoScale(
                outer=circle_with_radius(0.41),
                inner=circle_with_radius(0.39),
                tick=TickParameters(math.radians(45)),
                lines=[
                    LineParameters(0.02, scale_colour, cap=cairo.LINE_CAP_SQUARE),
                    LineParameters(0.018, gauge_shadow, cap=cairo.LINE_CAP_SQUARE)
                ],
                start=start,
                length=length,
                reading=reading,
            ),
        ])

    def draw(self, context: cairo.Context):
        self.widget.draw(context)


@pytest.mark.gfx
@approve_image
def test_cairo_simple_scale():
    return cairo_widget_test(CairoScale(
        outer=EllipseParameters(Coordinate(0.0, 0.0), major_curve=1.0 / 0.45, minor_radius=0.45, angle=0),
        inner=EllipseParameters(Coordinate(0.0, 0.0), major_curve=1.0 / 0.35, minor_radius=0.35, angle=0),
        tick=TickParameters(math.radians(45)),
        lines=[
            LineParameters(0.02, Colour(1.0, 1.0, 1.0), cap=cairo.LINE_CAP_SQUARE)
        ],
        start=math.pi / 2,
        length=math.pi * 3 / 2
    ))


@pytest.mark.gfx
@approve_image
def test_cairo_gauge_270():
    return cairo_widget_test(CairoGauge270(reading=lambda: Reading(0.600)))
