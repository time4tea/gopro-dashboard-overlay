from typing import Callable

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.annotation import AnnotationMode, EllipticAnnotation, create_texts, distribute
from gopro_overlay.widgets.cairo.cairo import CairoCache, CairoComposite, CairoWidget, NullCairoWidget
from gopro_overlay.widgets.cairo.colour import BLACK, WHITE, RED, Colour
from gopro_overlay.widgets.cairo.face import ToyFontFace
from gopro_overlay.widgets.cairo.gauge_marker import circle_with_radius
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.needle_sector import SectorNeedle, SectorArc
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.scale import CairoScale
from gopro_overlay.widgets.cairo.tick import TickParameters


class CairoGaugeDonutAnnotated(CairoWidget):
    def __init__(
            self,
            start=Angle(degrees=143),
            length=Angle(degrees=90),
            major_annotation_colour=BLACK,
            minor_annotation_colour=BLACK,
            major_tick_colour=BLACK,
            minor_tick_colour=BLACK,
            v_min=0,
            v_max=500,
            sectors=5,
            background_inner: Colour = WHITE.alpha(0.5),
            background_outer: Colour = WHITE.alpha(1.0),
            needle_colour=RED,
            arc_inner_colour=BLACK.alpha(0.1),
            arc_outer_colour=BLACK.alpha(0.8),
            reading: Callable[[], Reading] = lambda: Reading.full(),
            reading_arc_min: Callable[[], Reading] = lambda: Reading(0),
            reading_arc_max: Callable[[], Reading] = None,
    ):
        texts = create_texts(v_min, v_max, sectors)
        minor_texts, major_texts = distribute(texts, 2)

        outer_radius = 0.49

        stretch = 0.8

        step = abs(length / sectors)

        centre = Coordinate(x=0.0, y=0.0)

        # A bodge so that the numbers at the start and end have a background
        bodge_length_divisor = 2.5
        bodge = ((length / sectors) / bodge_length_divisor)

        background = SectorArc(
            inner=0.30,
            outer=0.50,
            inner_colour=background_inner,
            outer_colour=background_outer,
            start=start - bodge,
            length=length + (2 * bodge),
        )

        major_ticks = CairoScale(
            inner=circle_with_radius(0.43, centre),
            outer=circle_with_radius(outer_radius, centre),
            tick=TickParameters(step, 1, 0),
            lines=[LineParameters(6.0 / 400, colour=major_tick_colour)],
            start=start,
            length=length
        )

        minor_ticks = CairoScale(
            inner=circle_with_radius(0.46, centre),
            outer=circle_with_radius(outer_radius, centre),
            tick=TickParameters(step / 2.0, 2, 2),
            lines=[LineParameters(1.0 / 400, colour=minor_tick_colour)],
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
            start=start + (length / sectors),
            length=length - (length / sectors)
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

        needle = SectorNeedle(
            inner=circle_with_radius(0.31, centre),
            outer=circle_with_radius(outer_radius, centre),
            lines=[LineParameters(3.0 / 300, colour=needle_colour)],
            start=start,
            length=length,
            reading=reading
        )

        if reading_arc_max is None:
            arc = NullCairoWidget()
        else:
            arc = SectorArc(
                inner=0.30,
                outer=0.50,
                inner_colour=arc_inner_colour,
                outer_colour=arc_outer_colour,
                start=start,
                length=length,
                reading_min=reading_arc_min,
                reading_max=reading_arc_max,
            )

        self.widgets = [
            background,
            arc,
            CairoCache(
                CairoComposite([
                    major_ticks,
                    minor_ticks,
                    major_annotation,
                    minor_annotation, ]
                )
            ),
            needle,
        ]

    def draw(self, context: cairo.Context):
        [w.draw(context) for w in self.widgets]
