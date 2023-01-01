import math

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.picwl.picwl import EllipticBackground, Arc, EllipseParameters, WHITE, Cap, Colour, \
    EllipticScale, TickParameters, LineParameters, BLACK, Needle, NeedleParameter, RED, EllipticAnnotation, ToyFontFace, \
    AnnotationMode


class GaugeRound254:

    def __init__(self):
        value = lambda: 0.00
        minor_texts = [str(x) for x in range(0, 180, 20)]
        major_texts = [str(x) for x in range(10, 190, 20)]

        stretch = 0.8
        sectors = 17
        start = math.radians(143)
        length = math.radians(254)

        step = length / sectors

        centre = Coordinate(x=0.5, y=0.5)
        background = EllipticBackground(
            arc=Arc(
                EllipseParameters(centre, major_curve=1.0 / 0.5, minor_radius=0.5, angle=0.0),
            ),
            colour=WHITE
        )

        pin = Cap(
            centre=centre, radius=0.12, cfrom=WHITE, cto=Colour(0.5, 0.5, 0.5)
        )

        major_ticks = EllipticScale(
            inner=EllipseParameters(centre, major_curve=1.0 / 0.43, minor_radius=0.43, angle=0),
            outer=EllipseParameters(centre, major_curve=1.0 / 0.49, minor_radius=0.49, angle=0),
            tick=TickParameters(step, 1, 0),
            line=LineParameters(6.0 / 400, colour=BLACK),
            start=start,
            length=length
        )

        minor_ticks = EllipticScale(
            inner=EllipseParameters(centre, major_curve=1.0 / 0.46, minor_radius=0.46, angle=0),
            outer=EllipseParameters(centre, major_curve=1.0 / 0.49, minor_radius=0.49, angle=0),
            tick=TickParameters(step / 2.0, 2, 2),
            line=LineParameters(1.0 / 400, colour=BLACK),
            start=start,
            length=length
        )

        needle = Needle(
            centre=centre,
            value=value,
            start=start,
            length=length,
            tip=NeedleParameter(width=0.0175, length=0.46),
            rear=NeedleParameter(width=0.03, length=0.135),
            colour=RED
        )

        major_annotation = EllipticAnnotation(
            ellipse=EllipseParameters(centre=centre, major_curve=1.0 / 0.41, minor_radius=0.41, angle=0),
            tick=TickParameters(2.0 * step, 1, 0),
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
            ellipse=EllipseParameters(centre=centre, major_curve=1.0 / 0.41, minor_radius=0.41, angle=0),
            tick=TickParameters(2.0 * step, 1, 0),
            colour=BLACK,
            face=ToyFontFace("arial"),
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
            minor_annotation
        ]

    def draw(self, context: cairo.Context):
        [w.draw(context) for w in self.widgets]
