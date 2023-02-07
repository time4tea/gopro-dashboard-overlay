import pytest

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.bordered import Border, ShadowMode
from gopro_overlay.widgets.cairo.colour import BLACK, Colour, WHITE
from gopro_overlay.widgets.cairo.ellipse import Arc, EllipseParameters
from gopro_overlay.widgets.cairo.gauge_marker import CairoEllipticBackground
from tests.approval import approve_image
from tests.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_elliptic_background():
    return cairo_widget_test(
        widget=CairoEllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(Coordinate(x=0.25, y=0.25), major_curve=1.0 / 0.25, minor_radius=0.25)),
            colour=Colour(0.2, 0.5, 0.5)
        )
        , repeat=1)

@pytest.mark.cairo
@approve_image
def test_ellipse():
    return cairo_widget_test(
        widget=CairoEllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.5, minor_radius=0.5, angle=0.0),
                start=Angle.zero(),
                length=Angle.fullcircle()
            ),
            colour=BLACK.alpha(0.6),
            border=Border(width=0.005, depth=0.005, shadow=ShadowMode.ShadowIn, colour=Colour(0, 0, 0, 0.6))
        )
    )

@pytest.mark.cairo
@approve_image
def test_ellipse_with_border():
    return cairo_widget_test(
        widget=CairoEllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(
                    Coordinate(x=0.5, y=0.5),
                    major_curve=1.0 / 0.5,
                    minor_radius=0.5,
                    angle=0.0
                ),
                start=Angle.zero(),
                length=Angle.fullcircle()
            ),
            border=Border(
                width=0.01, depth=0.005, shadow=ShadowMode.ShadowEtchedOut, colour=BLACK
            ),
            colour=WHITE
        )
    )
