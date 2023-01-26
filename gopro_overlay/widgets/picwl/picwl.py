import dataclasses
import math
from enum import Enum, auto
from typing import List

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.cairo import saved
from gopro_overlay.widgets.picwl.bordered import Border, AbstractBordered
from gopro_overlay.widgets.picwl.box import abox
from gopro_overlay.widgets.picwl.colours import Colour, WHITE, BLACK
from gopro_overlay.widgets.picwl.constants import cos45
from gopro_overlay.widgets.picwl.face import FontFace


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
        context.set_source_rgba(*self.colour.rgba())
        context.set_line_cap(self.cap)
        context.set_line_width(self.width)


class EllipticScale:

    def __init__(self, inner: EllipseParameters, outer: EllipseParameters,
                 tick: TickParameters, line: LineParameters, start: float, length: float):
        self.inner = inner
        self.outer = outer
        self.tick = tick
        self.line = line
        self.start = start
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

                if thick == self.tick.skipped:
                    thick = 1
                else:
                    thick += 1

                    point_from = self.inner.get_point(self.inner * (self.start + value))
                    point_to = self.outer.get_point(self.outer * (self.start + value))

                    context.move_to(*point_from.tuple())
                    context.line_to(*point_to.tuple())

            context.stroke()


class EllipticBackground(AbstractBordered):
    def __init__(self, arc: Arc, colour: Colour = BLACK, border=Border.NONE()):
        super().__init__(border=border)
        self.arc = arc
        self.colour = colour

    def set_contents_path(self, context: cairo.Context):
        self.arc.draw(context)

    def draw_contents(self, context: cairo.Context):
        context.set_source_rgba(*self.colour.rgba())
        context.fill()


class Cap(AbstractBordered):
    def __init__(self, centre: Coordinate, radius: float, cfrom: Colour, cto: Colour):
        super().__init__()
        self.centre = centre
        self.radius = radius
        self.cfrom = cfrom
        self.cto = cto

        self.pattern: cairo.LinearGradient = None
        self.mask: cairo.RadialGradient = None

    def init(self):
        pattern = cairo.LinearGradient(-cos45, -cos45, cos45, cos45)
        pattern.add_color_stop_rgba(0.0, *self.cfrom.rgba())
        pattern.add_color_stop_rgba(1.0, *self.cto.rgba())

        mask = cairo.RadialGradient(
            0.0, 0.0, 0.0,
            0.0, 0.0, 1.0
        )
        mask.add_color_stop_rgba(0.0, *BLACK.rgba())
        mask.add_color_stop_rgba(1.0, *BLACK.rgba())
        mask.add_color_stop_rgba(1.00001, *BLACK.alpha(0).rgba())

        self.pattern = pattern
        self.mask = mask

    # def draw(self, context: cairo.Context):
    #     with saved(context):
    #         context.new_path()
    #         context.set_line_width(0.01)
    # self.set_contents_path(context)
    # context.close_path()
    # self.draw_contents(context)

    def set_contents_path(self, context: cairo.Context):
        context.arc(self.centre.x, self.centre.y, self.radius, 0.0, math.tau)

    def draw_contents(self, context: cairo.Context):
        if self.pattern is None:
            self.init()

        box = abox(*context.path_extents())
        print(box)
        r = 0.5 * (box.x2 - box.x1)

        matrix = context.get_matrix()
        matrix.xx = r
        matrix.x0 = matrix.x0 + 0.5 * (box.x1 + box.x2)
        matrix.yy = r
        matrix.y0 = matrix.y0 + 0.5 + (box.y1 + box.y2)

        context.set_matrix(matrix)
        context.set_source(self.pattern)
        context.mask(self.mask)
        # context.stroke()



class AnnotationMode(Enum):
    MovedInside = auto()
    MovedOutside = auto()
    MovedCentred = auto()
    Rotated = auto()
    Skewed = auto()


class EllipticAnnotation:

    def __init__(self,
                 ellipse: EllipseParameters,
                 tick: TickParameters,
                 colour: Colour,
                 face: FontFace,
                 mode: AnnotationMode,
                 texts: List[str],
                 height: float,
                 stretch: float,
                 start: float,
                 length: float):
        self.mode = mode
        self.texts = texts
        self.face = face
        self.colour = colour
        self.tick = tick
        self.ellipse = ellipse
        self.start = start
        self.original_length = length
        self.length = length + tick.step * 0.05
        self.height = height
        self.stretch = stretch

    def draw(self, context: cairo.Context):

        context.set_source_rgba(*self.colour.rgba())
        thick = self.tick.first

        for i in range(0, 1_000_000):
            angle = self.tick.step * i
            if angle > self.length:
                break
            if self.original_length < 0.0:
                angle = -angle
            if thick == self.tick.skipped:
                thick = 1
            else:
                thick += 1
                angle = self.start + angle
                print(angle)
                point = self.ellipse.get_point(self.ellipse * angle)

                print(point)

                if i >= len(self.texts):
                    break

                text = self.texts[i]
                extents = self.face.text_extents(context, text)

                with saved(context):
                    if extents.height > 0.0:
                        gain = self.height / extents.height

                        context.translate(*point.tuple())

                        if self.mode == AnnotationMode.MovedInside:
                            context.translate(
                                (-extents.width * 0.5 * gain * math.cos(angle)),
                                (-extents.height * 0.5 * gain * math.sin(angle))
                            )
                        elif self.mode == AnnotationMode.MovedOutside:
                            raise NotImplementedError("Moved Outside")
                        elif self.mode == AnnotationMode.MovedCentred:
                            # nothing to do
                            pass
                        elif self.mode == AnnotationMode.Rotated:
                            raise NotImplementedError("Rotated")
                        elif self.mode == AnnotationMode.Skewed:
                            raise NotImplementedError("Skewed")

                        context.scale(gain * self.stretch, gain)
                        context.move_to(
                            -(extents.x_bearing + extents.width) * 0.5,
                            -(extents.y_bearing + extents.height) * 0.5
                        )

                        self.face.show(context, text)
