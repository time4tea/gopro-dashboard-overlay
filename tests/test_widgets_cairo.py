import math

from gopro_overlay.dimensions import Dimension
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.picwl.picwl import EllipseParameters, Colour, BLACK, RED, Arc, TickParameters, \
    LineParameters, EllipticScale, EllipticBackground, Cap, NeedleParameter, Needle, AnnotationMode, ToyFontFace, \
    EllipticAnnotation, GaugeRound254
from gopro_overlay.widgets.cairo import CairoWidget
from tests.approval import approve_image
from tests.test_widgets import time_rendering


def cairo_widget_test(widgets, repeat=100):
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            CairoWidget(size=Dimension(500, 500), widgets=widgets)
        ],
        repeat=repeat
    )


@approve_image
def test_ellipse():
    return cairo_widget_test(widgets=[
        EllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.5, minor_radius=0.5, angle=0.0),
                start=0.0, length=math.pi
            ),
            colour=BLACK
        )
    ])


@approve_image
def test_cap():
    return cairo_widget_test(widgets=[
        Cap(
            centre=Coordinate(0.0, 0.0),
            radius=0.5,
            cfrom=Colour(1.0, 1.0, 1.0),
            cto=Colour(0.5, 0.5, 0.5)
        )
    ], repeat=1)


@approve_image
def test_scale():
    start = math.radians(143)
    length = math.radians(254)
    step = math.pi / 12

    return cairo_widget_test(widgets=[
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
    ])


@approve_image
def test_needle():
    return cairo_widget_test(widgets=[
        Needle(
            value=lambda: 0.0,
            centre=Coordinate(0.5, 0.5),
            start=math.radians(143),
            length=math.radians(254),
            tip=NeedleParameter(width=0.0175, length=0.46),
            rear=NeedleParameter(width=0.03, length=0.135),
            colour=RED
        )
    ])


@approve_image
def test_annotation():
    sectors = 17
    step = math.radians(254) / sectors

    return cairo_widget_test(widgets=[
        EllipticAnnotation(
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
        ),
    ], repeat=1)


@approve_image
def test_gauge_round_254():
    return cairo_widget_test(widgets=[
        GaugeRound254()
    ], repeat=1)


@approve_image
def test_elliptic_background():
    return cairo_widget_test(widgets=[
        EllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(Coordinate(x=0.25, y=0.25), major_curve=1.0 / 0.25, minor_radius=0.25)),
            colour=Colour(0.2, 0.5, 0.5)
        )
    ], repeat=1)
