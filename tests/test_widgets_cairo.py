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


def tiny(f: float) -> bool:
    return abs(f) < 0.000001


@dataclasses.dataclass(frozen=True)
class Colour:
    r: int
    g: int
    b: int
    a: int = 255

    def tuple(self):
        return self.r, self.g, self.b, self.a

    def cairo(self):
        return self.r, self.g, self.b

    @staticmethod
    def BLACK():
        return Colour(0, 0, 0)

    @staticmethod
    def WHITE():
        return Colour(255, 255, 255)


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
            context.save()
            try:
                context.translate(*self.ellipse.centre.tuple())
                context.rotate(self.ellipse.angle)
                context.scale(1.0 / self.ellipse.major_curve, self.ellipse.minor_radius)
                if self.length > 0.0:
                    context.arc(0.0, 0.0, 1.0, self.start, to)
                else:
                    context.arc_negative(0.0, 0.0, 1.0, self.start, to)
            finally:
                context.restore()


class EllipticBackground:
    def __init__(self,
                 arc: Arc,
                 colour: Colour = Colour.BLACK):
        self.arc = arc
        self.colour = colour

    def draw(self, context: cairo.Context):
        self.arc.draw(context)

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
                    colour=Colour.BLACK()
                )
            ])
        ],
        repeat=100
    )
