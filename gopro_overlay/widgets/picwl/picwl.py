import colorsys
import dataclasses
import math
from enum import Enum, auto
from typing import Callable, Tuple, List

import cairo
from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.journey import Journey

from gopro_overlay.point import Coordinate, Point
from gopro_overlay.widgets.cairo import saved, to_pillow


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

            ctx.set_source_rgba(*Colour(0.3, 0.2, 0.5).rgba())
            ctx.set_line_width(line_width)
            ctx.stroke_preserve()

            ctx.set_source_rgba(*WHITE.rgba())
            ctx.set_line_width(line_width / 4)
            ctx.stroke()

            self.drawn = True

        image.alpha_composite(to_pillow(self.surface), (0, 0))


@dataclasses.dataclass(frozen=True)
class HLSColour:
    h: float
    l: float
    s: float
    a: float

    def lighten(self, by: float) -> 'HLSColour':
        return HLSColour(self.h, min(self.l + by, 1.0), self.s, self.a)

    def darken(self, by: float) -> 'HLSColour':
        return HLSColour(self.h, max(self.l - by, 1.0), self.s, self.a)

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


cos45 = math.sqrt(2.0) * 0.5


@dataclasses.dataclass(frozen=True)
class Box:
    x1: float
    y1: float
    x2: float
    y2: float


def abox(x1, y1, x2, y2):
    return Box(x1, y1, x2, y2)


class ShadowMode(Enum):
    ShadowNone = auto()
    ShadowIn = auto()
    ShadowOut = auto()
    ShadowEtchedIn = auto()
    ShadowEtchedOut = auto()


class DrawingAction(Enum):
    Region = auto()
    Line = auto()
    Contents = auto()


darkenBy = 1.0 / 3
lightenBy = 1.0 / 3


@dataclasses.dataclass
class Border:
    width: float
    depth: float
    shadow: ShadowMode
    colour: Colour

    @staticmethod
    def NONE() -> 'Border':
        return Border(width=0.0, depth=0.0, shadow=ShadowMode.ShadowNone, colour=BLACK)


class AbstractBordered:
    def __init__(self, border: Border = Border.NONE()):
        self.border_width = border.width
        self.border_depth = border.depth
        self.border_shadow = border.shadow
        self.colour = border.colour
        self.scaled = True

    def set_contents_path(self, context: cairo.Context):
        pass

    def draw_contents(self, context: cairo.Context):
        pass

    def draw(self, context: cairo.Context):

        if self.border_width > 0:
            shadow_depth = self.border_depth
        else:
            shadow_depth = 0.0

        with saved(context):
            context.new_path()
            self.set_contents_path(context)
            context.close_path()

            box = abox(*context.path_extents())

            extent = abs(box.x2 - box.x1)

            print(box)

            box_centre = Coordinate(
                x=(box.x2 + box.x1) * 0.5,
                y=(box.y2 + box.y1) * 0.5
            )

            def _draw(shift: float, bound: float, width: float, action: DrawingAction = DrawingAction.Line):
                F = (bound - width) / extent
                S = shift * shadow_depth * 0.5

                FX = F
                FY = F

                print(f"F = {F} S={S}")

                context.new_path()
                context.scale(FX, FY)
                context.translate(
                    box_centre.x * (1.0 / FX - 1.0) + S * cos45 / FX,
                    box_centre.y * (1.0 / FY - 1.0) + S * cos45 / FY
                )
                context.append_path(path)
                context.set_line_width(width / F)

                if action == DrawingAction.Line:
                    context.stroke()
                elif action == DrawingAction.Region:
                    context.fill()
                elif action == DrawingAction.Contents:
                    print("Draw Contents")
                    self.draw_contents(context)

            if self.scaled:
                outer_size = extent
                inner_size = extent - 2.0 * self.border_width
                middle_size = outer_size
            else:
                inner_size = extent
                outer_size = extent + 2.0 * self.border_width

                if self.border_shadow == ShadowMode.ShadowNone:
                    middle_size = outer_size
                elif self.border_shadow == ShadowMode.ShadowIn:
                    outer_size = outer_size + 2.0 * shadow_depth
                    middle_size = outer_size
                elif self.border_shadow == ShadowMode.ShadowOut:
                    outer_size = outer_size + shadow_depth
                    middle_size = outer_size - 2.0 * shadow_depth
                elif self.border_shadow in [ShadowMode.ShadowEtchedIn, ShadowMode.ShadowEtchedOut]:
                    outer_size = outer_size + 2.0 * shadow_depth
                    middle_size = outer_size - 2.0 * shadow_depth

            def set_normal():
                context.set_source_rgba(*self.colour.rgba())

            def set_light():
                context.set_source_rgba(*self.colour.lighten(lightenBy).rgba())

            def set_dark():
                context.set_source_rgba(*self.colour.darken(darkenBy).rgba())

            if inner_size > 0:
                path = context.copy_path()

                if self.border_shadow == ShadowMode.ShadowNone:
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                elif self.border_shadow == ShadowMode.ShadowIn:
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                    set_dark()
                    _draw(-1.0, inner_size + shadow_depth, shadow_depth)
                    set_light()
                    _draw(1.0, inner_size + shadow_depth, shadow_depth)
                elif self.border_shadow == ShadowMode.ShadowOut:
                    set_light()
                    _draw(-1.0, outer_size - shadow_depth, shadow_depth)
                    set_dark()
                    _draw(1.0, outer_size - shadow_depth, shadow_depth)
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                elif self.border_shadow == ShadowMode.ShadowEtchedIn:
                    set_dark()
                    _draw(-1.0, outer_size - shadow_depth, shadow_depth)
                    set_light()
                    _draw(1.0, outer_size - shadow_depth, shadow_depth)
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                    set_light()
                    _draw(-1.0, inner_size + shadow_depth, shadow_depth)
                    set_dark()
                    _draw(1.0, inner_size + shadow_depth, shadow_depth)
                elif self.border_shadow == ShadowMode.ShadowEtchedOut:
                    set_light()
                    _draw(-1.0, outer_size - shadow_depth, shadow_depth)
                    set_dark()
                    _draw(1.0, outer_size - shadow_depth, shadow_depth)
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                    set_dark()
                    _draw(-1.0, inner_size + shadow_depth, shadow_depth)
                    set_light()
                    _draw(1.0, inner_size + shadow_depth, shadow_depth)
                _draw(0.0, inner_size, 0.0, DrawingAction.Contents)


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


@dataclasses.dataclass(frozen=True)
class NeedleParameter:
    width: float
    length: float
    cap: cairo.LineCap = cairo.LINE_CAP_BUTT

    @property
    def radius(self):
        return self.width / 2.0


class Needle:

    def __init__(self, centre: Coordinate,
                 value: Callable[[], float],
                 start: float, length: float,
                 tip: NeedleParameter, rear: NeedleParameter,
                 colour: Colour):
        self.centre = centre
        self.colour = colour
        self.rear = rear
        self.tip = tip
        self.length = length
        self.start = start
        self.value = value

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
            context.set_source_rgba(*self.colour.rgba())

            context.fill()


class AnnotationMode(Enum):
    MovedInside = auto()
    MovedOutside = auto()
    MovedCentred = auto()
    Rotated = auto()
    Skewed = auto()


class FontFace:

    def text_extents(self, context: cairo.Context, text: str) -> cairo.TextExtents:
        raise NotImplementedError()

    def show(self, context: cairo.Context, text: str):
        raise NotImplementedError()


class PangoFontFace(FontFace):
    pass


class ToyFontFace(FontFace):

    def __init__(self, family: str, slant: cairo.FontSlant = cairo.FONT_SLANT_NORMAL,
                 weight: cairo.FontWeight = cairo.FONT_WEIGHT_NORMAL):
        self.face = cairo.ToyFontFace(family, slant, weight)

    def text_extents(self, context: cairo.Context, text: str) -> cairo.TextExtents:
        context.set_font_face(self.face)
        return context.text_extents(text)

    def show(self, context: cairo.Context, text: str):
        context.set_font_face(self.face)
        context.show_text(text)


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
