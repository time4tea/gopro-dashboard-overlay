import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.annotation import AnnotationMode, EllipticAnnotation
from gopro_overlay.widgets.cairo.colour import BLACK, WHITE, RED
from gopro_overlay.widgets.cairo.ellipse import Arc, EllipseParameters
from gopro_overlay.widgets.cairo.face import ToyFontFace
from gopro_overlay.widgets.cairo.gauge import CairoEllipticBackground, circle_with_radius
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.needle import Needle, NeedleParameter
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.scale import CairoScale
from gopro_overlay.widgets.cairo.tick import TickParameters


class GaugeRound254:

    def __init__(self):
        value = lambda: Reading(3.0 / 17)
        minor_texts = [str(x) for x in range(0, 180, 20)]
        major_texts = [str(x) for x in range(10, 190, 20)]

        stretch = 0.8
        sectors = 17
        start = Angle(degrees=143)
        length = Angle(degrees=254)

        step = length / sectors

        centre = Coordinate(x=0.5, y=0.5)
        background = CairoEllipticBackground(
            arc=Arc(
                circle_with_radius(0.5, centre),
            ),
            colour=WHITE.alpha(0.7)
        )

        major_ticks = CairoScale(
            inner=circle_with_radius(0.43, centre),
            outer=circle_with_radius(0.49, centre),
            tick=TickParameters(step, 1, 0),
            lines=[LineParameters(6.0 / 400, colour=BLACK)],
            start=start,
            length=length
        )

        minor_ticks = CairoScale(
            inner=circle_with_radius(0.46, centre),
            outer=circle_with_radius(0.49, centre),
            tick=TickParameters(step / 2.0, 2, 2),
            lines=[LineParameters(1.0 / 400, colour=BLACK)],
            start=start,
            length=length
        )

        needle = Needle(
            centre=centre,
            reading=value,
            start=start,
            length=length,
            tip=NeedleParameter(width=0.0175, length=0.46),
            rear=NeedleParameter(width=0.03, length=0.135),
            colour=RED
        )

        text_radius = 0.41
        major_annotation = EllipticAnnotation(
            ellipse=circle_with_radius(text_radius, centre),
            tick=TickParameters(step * 2.0, 1, 0),
            colour=BLACK,
            face=ToyFontFace("arial"),
            mode=AnnotationMode.MovedInside,
            texts=major_texts,
            height=0.05,
            stretch=stretch,
            start=start + step,
            length=length - step
        )

        minor_annotation = EllipticAnnotation(
            ellipse=circle_with_radius(text_radius, centre),
            tick=TickParameters(step * 2.0, 1, 0),
            colour=BLACK,
            face=ToyFontFace("Roboto-Medium"),
            mode=AnnotationMode.MovedInside,
            texts=minor_texts,
            height=0.035,
            stretch=stretch,
            start=start,
            length=length
        )

        self.widgets = [
            background,
            major_ticks,
            minor_ticks,
            needle,
            major_annotation,
            minor_annotation,
        ]

    def draw(self, context: cairo.Context):
        [w.draw(context) for w in self.widgets]
