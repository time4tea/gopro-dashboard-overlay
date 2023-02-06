import math

import cairo

from gopro_overlay.dimensions import Dimension
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.cairo import saved, CairoWidget, CairoAdapter
from gopro_overlay.widgets.picwl.bordered import Border, ShadowMode
from gopro_overlay.widgets.picwl.colours import BLACK, RED
from gopro_overlay.widgets.picwl.face import ToyFontFace
from gopro_overlay.widgets.picwl.gauge_round_254 import GaugeRound254
from gopro_overlay.widgets.picwl.needle import Needle, NeedleParameter
from gopro_overlay.widgets.picwl.picwl import EllipseParameters, Colour, Arc, TickParameters, \
    LineParameters, EllipticScale, EllipticBackground, Cap, AnnotationMode, EllipticAnnotation, WHITE
from tests.approval import approve_image
from tests.test_widgets import time_rendering


class CairoTranslate(CairoWidget):
    def __init__(self, by: Coordinate, widget: CairoWidget):
        self.by = by
        self.widget = widget

    def draw(self, context: cairo.Context):
        with saved(context):
            context.translate(*self.by.tuple())
            self.widget.draw(context)


class CairoCompose(CairoWidget):
    def __init__(self, widgets):
        self.widgets = widgets

    def draw(self, context: cairo.Context):
        for w in self.widgets:
            w.draw(context)


def cairo_widget_test(widget, repeat=1):
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            CairoAdapter(
                size=Dimension(500, 500),
                widget=CairoTranslate(by=Coordinate(-0.5, -0.5), widget=widget)
            )
        ],
        repeat=repeat
    )


@approve_image
def test_ellipse():
    return cairo_widget_test(
        widget=EllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.5, minor_radius=0.5, angle=0.0),
                start=0.0, length=math.pi * 2
            ),
            colour=BLACK.alpha(0.6),
            border=Border(width=0.005, depth=0.005, shadow=ShadowMode.ShadowIn, colour=Colour(0, 0, 0, 0.6))
        )
    )


@approve_image
def test_ellipse_with_border():
    return cairo_widget_test(
        widget=EllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(
                    Coordinate(x=0.5, y=0.5),
                    major_curve=1.0 / 0.5,
                    minor_radius=0.5,
                    angle=0.0
                ),
                start=0.0, length=math.tau
            ),
            border=Border(
                width=0.01, depth=0.005, shadow=ShadowMode.ShadowEtchedOut, colour=BLACK
            ),
            colour=WHITE
        )
    )


@approve_image
def test_cap():
    return cairo_widget_test(
        widget=Cap(
            centre=Coordinate(0.0, 0.0),
            radius=0.5,
            cfrom=Colour(1.0, 1.0, 1.0),
            cto=Colour(0.5, 0.5, 0.5)
        )
    )


@approve_image
def test_scale():
    start = math.radians(143)
    length = math.radians(254)
    step = math.pi / 12

    return cairo_widget_test(
        widget=CairoCompose(
            widgets=[
                EllipticScale(
                    inner=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.43, minor_radius=0.43, angle=0.0),
                    outer=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.49, minor_radius=0.49, angle=0.0),
                    tick=TickParameters(step=step, first=1, skipped=1000),
                    length=length,
                    start=start,
                    line=LineParameters(
                        width=6.0 / 400.0,
                        colour=BLACK
                    )
                ),
                EllipticScale(
                    inner=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.46, minor_radius=0.46, angle=0.0),
                    outer=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.49, minor_radius=0.49, angle=0.0),
                    tick=TickParameters(step=step / 2.0, first=2, skipped=2),
                    length=length,
                    start=start,
                    line=LineParameters(
                        width=1.0 / 400.0,
                        colour=BLACK
                    )
                ),
            ]
        )
    )


@approve_image
def test_needle():
    return cairo_widget_test(
        widget=Needle(
            value=lambda: 0.0,
            centre=Coordinate(0.5, 0.5),
            start=math.radians(143),
            length=math.radians(254),
            tip=NeedleParameter(width=0.0175, length=0.46),
            rear=NeedleParameter(width=0.03, length=0.135),
            colour=RED
        )
    )


@approve_image
def test_annotation():
    sectors = 17
    step = math.radians(254) / sectors

    return cairo_widget_test(widget=EllipticAnnotation(
        ellipse=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.41, minor_radius=0.41,
                                  angle=math.tau),
        tick=TickParameters(step=(math.pi / 12) / 2.0, first=1, skipped=2),
        colour=BLACK,
        face=ToyFontFace("arial"),
        mode=AnnotationMode.MovedInside,
        texts=[str(x) for x in range(0, 180, 10)],
        height=0.05,
        stretch=0.8,
        start=0.0 + step,
        length=math.tau - step
    ), repeat=1)


@approve_image
def test_gauge_round_254():
    return cairo_widget_test(widget=GaugeRound254(), repeat=1)


class GaugeElliptic180:

    def __init__(self):
        bg = Colour(1.0, 0.0, 0.0)

        length = math.pi
        first = math.pi
        excess = math.pi / 30.0
        y = 0.225

        inner = EllipseParameters(Coordinate(x=-0.045, y=y), 1.0 / 0.40, 0.31, -math.pi / 5.0)
        outer = EllipseParameters(Coordinate(x=-0.020, y=y), 1.0 / 0.43, 0.36, -math.pi / 4.0)

        background = EllipticBackground(
            Arc(
                ellipse=EllipseParameters(Coordinate(0, y), 1.0 / 0.5, 0.5, 0.0),
                start=first - excess,
                length=length + excess * 2.0,
            ),
            colour=bg
        )

        scale_area = EllipticBackground(
            Arc(
                ellipse=EllipseParameters(

                )
            )
        )
        self.widgets = [
            background
        ]

    def draw(self, context: cairo.Context):
        [w.draw(context) for w in self.widgets]


def test_gauge_elliptic_180():
    return cairo_widget_test(widget=GaugeElliptic180(), repeat=1)


@approve_image
def test_elliptic_background():
    return cairo_widget_test(
        widget=EllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(Coordinate(x=0.25, y=0.25), major_curve=1.0 / 0.25, minor_radius=0.25)),
            colour=Colour(0.2, 0.5, 0.5)
        )
        , repeat=1)
