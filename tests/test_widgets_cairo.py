import contextlib
import dataclasses
import math
from typing import Callable

import cairo
from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.exceptions import Defect
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.journey import Journey
from gopro_overlay.point import Point, Coordinate
from gopro_overlay.widgets.widgets import Translate
from tests.approval import approve_image
from tests.test_widgets import time_rendering


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

            return self.centre.x + cos_angle * math.cos(self.angle) / self.major_curve - sin_angle * math.sin(self.angle) * self.minor_radius

    def get_y(self, angle) -> float:
        if tiny(angle):
            beta, cos_gamma = self.cos_gamma(angle)
            return self.centre.y + self.minor_radius * math.sin(beta) / cos_gamma
        else:
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)

            return self.centre.y + cos_angle * math.sin(self.angle) / self.major_curve + sin_angle * math.cos(self.angle) * self.minor_radius

    def get(self, angle) -> Coordinate:
        return Coordinate(x=self.get_x(angle), y=self.get_y(angle))

    def get_point(self, angle):
        return self.centre + self.get_relative_point(angle)

    def get_relative_point(self, angle) -> Coordinate:
        if tiny(self.major_curve):
            beta = angle + self.angle
            cos_gamma = abs(math.cos(math.pi / 2.0 + self.angle - beta))
            if tiny(cos_gamma):
                raise ValueError("infinite coordinate")
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


@contextlib.contextmanager
def saved(context: cairo.Context):
    context.save()
    try:
        yield
    finally:
        context.restore()


@dataclasses.dataclass(frozen=True)
class Colour:
    r: float
    g: float
    b: float
    a: float = 1.0

    def tuple(self):
        return self.r, self.g, self.b, self.a

    def cairo(self):
        return self.r, self.g, self.b


BLACK = Colour(0.0, 0.0, 0.0)
WHITE = Colour(1.0, 1.0, 1.0)
RED = Colour(1.0, 0.0, 0.0)


class Arc:
    def __init__(self, ellipse: EllipseParameters, start: float = 0.0, length=2 * math.pi):
        self.ellipse = ellipse
        self.start = start
        self.length = length

    def draw(self, context: cairo.Context):
        to = self.start + self.length
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


@dataclasses.dataclass(frozen=True)
class TickParameters:
    step: float
    first: int
    skipped: int


@dataclasses.dataclass(frozen=True)
class LineParameters:
    width: float
    colour: Colour = WHITE
    cap: cairo.LineCap = cairo.LINE_CAP_BUTT

    def apply_to(self, context: cairo.Context):
        context.set_source_rgb(*self.colour.cairo())
        context.set_line_cap(self.cap)
        context.set_line_width(self.width)


class EllipticScale:

    def __init__(self, inner: EllipseParameters, outer: EllipseParameters,
                 tick: TickParameters, line: LineParameters, length: float):
        self.inner = inner
        self.outer = outer
        self.tick = tick
        self.line = line
        self.start = 0.0
        self.length = length + tick.step * 0.05

    def draw(self, context: cairo.Context):
        with saved(context):
            context.new_path()

            self.line.apply_to(context)

            thick = self.tick.first

            for i in range(0, 1000):
                value = self.tick.step * i
                if value >= self.length:
                    break

                if value == self.tick.skipped:
                    thick = 1
                else:
                    thick += 1

                    point_from = self.inner.get_point(self.inner * (self.start + value))
                    point_to = self.outer.get_point(self.outer * (self.start + value))

                    context.move_to(*point_from.tuple())
                    context.line_to(*point_to.tuple())

            context.stroke()


class EllipticBackground:
    def __init__(self,
                 arc: Arc,
                 colour: Colour = BLACK):
        self.arc = arc
        self.colour = colour

    def draw(self, context: cairo.Context):
        self.arc.draw(context)

        context.set_source_rgb(*self.colour.cairo())
        context.fill()


cos45 = math.sqrt(2.0) * 0.5


class Cap:
    def __init__(self, centre: Coordinate, radius: float, cfrom: Colour, cto: Colour):
        self.centre = centre
        self.radius = radius
        self.cfrom = cfrom
        self.cto = cto

        self.pattern = None
        self.mask = None

    def init(self):
        pattern = cairo.LinearGradient(-cos45, -cos45, cos45, cos45)
        pattern.add_color_stop_rgb(0.0, *self.cfrom.cairo())
        pattern.add_color_stop_rgb(1.0, *self.cto.cairo())

        mask = cairo.RadialGradient(
            0.0, 0.0, 0.0,
            0.0, 0.0, 1.0
        )
        mask.add_color_stop_rgba(0.0, 0.0, 0.0, 0.0, 1.0)
        mask.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 1.0)
        mask.add_color_stop_rgba(1.01, 0.0, 0.0, 0.0, 1.0)

        self.pattern = pattern
        self.mask = mask

    def draw(self, context: cairo.Context):
        if self.pattern is None:
            self.init()

        context.arc(self.centre.x, self.centre.y, self.radius, 0.0, math.tau)

        x1, y1, x2, y2 = context.path_extents()
        r = 0.5 * (x2 - x1)

        matrix = context.get_matrix()
        matrix.xx = r
        matrix.x0 = matrix.x0 + 0.5 * (x1 + x2)
        matrix.yy = r
        matrix.y0 = matrix.y0 + 0.5 + (y1 + y2)

        context.set_matrix(matrix)
        context.set_source(self.pattern)
        context.mask(self.mask)


@dataclasses.dataclass(frozen=True)
class NeedleParameter:
    width: float
    length: float
    cap: cairo.LineCap = cairo.LINE_CAP_BUTT

    @property
    def radius(self):
        return self.width / 2.0


class Needle:

    def __init__(self, centre: Coordinate, start: float, length: float, tip: NeedleParameter, rear: NeedleParameter, colour: Colour):
        self.centre = centre
        self.colour = colour
        self.rear = rear
        self.tip = tip
        self.length = length
        self.start = start
        self.value = lambda: 0.0

    def draw(self, context: cairo.Context):
        with saved(context):
            context.new_path()
            context.translate(*self.centre.tuple())
            context.rotate(self.start + self.value() * self.length)

            tip = self.tip
            rear = self.rear

            if tip.cap == cairo.LINE_CAP_BUTT:
                context.move_to(tip.length, -tip.radius)
                context.line_to(tip.length, tip.radius)
            elif tip.cap == cairo.LINE_CAP_ROUND:

                angle = math.atan2(
                    tip.radius - rear.radius,
                    tip.length + rear.length
                )
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                context.move_to(tip.length + tip.radius * sin_angle, -tip.radius * cos_angle)
                context.arc(tip.length, 0.0, tip.radius, angle - math.pi / 2.0, math.pi / 2.0 - angle)
                context.line_to(tip.length + tip.radius * sin_angle, tip.radius * cos_angle)

            elif tip.cap == cairo.LINE_CAP_SQUARE:
                context.move_to(tip.length, -tip.radius)
                context.line_to(tip.length + tip.radius * math.sqrt(2.0), 0.0)
                context.line_to(tip.length, tip.radius)
            else:
                raise ValueError("Unsupported needle tip type")

            if rear.cap == cairo.LINE_CAP_BUTT:
                context.line_to(-rear.length, rear.radius)
                context.line_to(-rear.length, -rear.radius)
            elif tip.cap == cairo.LINE_CAP_ROUND:
                angle = math.atan2(
                    rear.radius - tip.radius,
                    tip.length + rear.length
                )
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                context.line_to(-rear.length - rear.radius * sin_angle, rear.radius * cos_angle)
                context.arc(-rear.length, 0.0, rear.radius, math.pi / 2.0 - angle, angle - math.pi / 2.0)
                context.line_to(-rear.length - rear.radius * sin_angle, -rear.radius * cos_angle)

            elif tip.cap == cairo.LINE_CAP_SQUARE:
                context.line_to(-rear.length, rear.radius)
                context.line_to(-rear.length - rear.radius * math.sqrt(2.0), 0.0)
                context.line_to(-rear.length, -rear.radius)
            else:
                raise ValueError("Unsupported needle rear type")

            context.close_path()
            context.set_source_rgb(*self.colour.cairo())


            context.fill()


def to_pillow(surface: cairo.ImageSurface) -> Image:
    size = (surface.get_width(), surface.get_height())
    stride = surface.get_stride()

    format = surface.get_format()
    if format != cairo.FORMAT_ARGB32:
        raise Defect(f"Only support ARGB32 images, not {format}")

    with surface.get_data() as memory:
        return Image.frombuffer("RGBA", size, memory.tobytes(), 'raw', "BGRa", stride)


class CairoWidget:

    def __init__(self, size: Dimension, widgets):
        self.size = size
        self.widgets = widgets

    def draw(self, image: Image, draw: ImageDraw):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size.x, self.size.y)
        ctx = cairo.Context(surface)
        ctx.scale(surface.get_width(), surface.get_height())

        for widget in self.widgets:
            widget.draw(ctx)

        image.alpha_composite(to_pillow(surface), (0, 0))


@approve_image
def test_ellipse():
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            CairoWidget(size=Dimension(500, 500), widgets=[
                EllipticBackground(
                    arc=Arc(
                        ellipse=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.5, minor_radius=0.5, angle=0.0),
                        start=0.0, length=math.pi
                    ),
                    colour=BLACK
                )
            ])
        ],
        repeat=100
    )


@approve_image
def test_cap():
    return time_rendering(
        widgets=[
            Translate(
                at=Coordinate(x=50, y=50),
                widget=CairoWidget(size=Dimension(200, 200), widgets=[
                    Cap(
                        centre=Coordinate(0.0, 0.0),
                        radius=1.0,
                        cfrom=Colour(1.0, 1.0, 1.0),
                        cto=Colour(0.5, 0.5, 0.5)
                    )
                ]))
        ], repeat=1
    )


@approve_image
def test_scale():
    return time_rendering(
        widgets=[
            CairoWidget(size=Dimension(500, 500), widgets=[
                EllipticScale(
                    inner=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.43, minor_radius=0.43, angle=0.0),
                    outer=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.49, minor_radius=0.49, angle=0.0),
                    tick=TickParameters(step=math.pi / 12, first=1, skipped=1000),
                    length=2 * math.pi,
                    line=LineParameters(
                        width=6.0 / 400.0,
                    )
                ),
                EllipticScale(
                    inner=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.43, minor_radius=0.43, angle=0.0),
                    outer=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.49, minor_radius=0.49, angle=0.0),
                    tick=TickParameters(step=(math.pi / 12) / 2.0, first=1, skipped=2),
                    length=2 * math.pi,
                    line=LineParameters(
                        width=1.0 / 400.0,
                        colour=BLACK
                    )
                ),
            ])
        ], repeat=1
    )


@approve_image
def test_needle():
    return time_rendering(
        dimensions=Dimension(500, 500),
        widgets=[
            CairoWidget(size=Dimension(500, 500), widgets=[
                Needle(
                    centre=Coordinate(0.5, 0.5),
                    start=math.radians(36),
                    length=math.radians(254),
                    tip=NeedleParameter(width=0.0175, length=0.46),
                    rear=NeedleParameter(width=0.03, length=0.135),
                    colour=RED
                )
            ])
        ],
        repeat=1
    )
