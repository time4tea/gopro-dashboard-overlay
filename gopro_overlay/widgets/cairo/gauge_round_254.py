from typing import Callable

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.annotation import AnnotationMode, EllipticAnnotation, create_texts, distribute
from gopro_overlay.widgets.cairo.background import CairoEllipticBackground
from gopro_overlay.widgets.cairo.cairo import CairoCache, CairoComposite
from gopro_overlay.widgets.cairo.colour import BLACK, WHITE, RED, Colour
from gopro_overlay.widgets.cairo.ellipse import Arc
from gopro_overlay.widgets.cairo.face import ToyFontFace
from gopro_overlay.widgets.cairo.gauge_marker import circle_with_radius
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.needle import Needle, NeedleParameter
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.scale import CairoScale
from gopro_overlay.widgets.cairo.tick import TickParameters


class GaugeRoundNeedleAnnotated:
    def __init__(
            self,
            start=Angle(degrees=143),
            length=Angle(degrees=254),
            major_annotation_colour=BLACK,
            minor_annotation_colour=BLACK,
            v_min=0,
            v_max=170,
            sectors=17,
            background_colour: Colour = WHITE.alpha(0.7),
            needle_colour = RED,
            reading: Callable[[], Reading] = lambda: Reading.full(),
    ):

        texts = create_texts(v_min, v_max, sectors)
        minor_texts, major_texts = distribute(texts, 2)

        stretch = 0.8

        step = length / sectors

        centre = Coordinate(x=0.0, y=0.0)
        background = CairoEllipticBackground(
            arc=Arc(
                circle_with_radius(0.5, centre),
            ),
            colour=background_colour,
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

        text_radius = 0.41

        major_annotation = EllipticAnnotation(
            ellipse=circle_with_radius(text_radius, centre),
            tick=TickParameters(step * 2.0, 1, 0),
            colour=major_annotation_colour,
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
            colour=minor_annotation_colour,
            face=ToyFontFace("Roboto-Medium"),
            mode=AnnotationMode.MovedInside,
            texts=minor_texts,
            height=0.035,
            stretch=stretch,
            start=start,
            length=length
        )

        needle = Needle(
            centre=centre,
            reading=reading,
            start=start,
            length=length,
            tip=NeedleParameter(width=0.0175, length=0.46),
            rear=NeedleParameter(width=0.03, length=0.135),
            colour=needle_colour,
        )

        self.widgets = [
            CairoCache(
                CairoComposite(
                    [background,
                    major_ticks,
                    minor_ticks,
                    major_annotation,
                    minor_annotation,]
                )
            ),
            needle,
        ]

    def draw(self, context: cairo.Context):
        [w.draw(context) for w in self.widgets]
