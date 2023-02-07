import pytest

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.bordered import Border, ShadowMode
from gopro_overlay.widgets.cairo.cairo import CairoCache
from gopro_overlay.widgets.cairo.colour import BLACK, Colour, WHITE
from gopro_overlay.widgets.cairo.ellipse import Arc, EllipseParameters
from gopro_overlay.widgets.cairo.background import CairoEllipticBackground
from tests.approval import approve_image
from tests.widgets.cairo.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_elliptic_background():
    return cairo_widget_test(
        widget=CairoCache(CairoEllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(Coordinate(x=-0.25, y=-0.25), major_curve=1.0 / 0.25, minor_radius=0.25)),
            colour=Colour(0.2, 0.5, 0.5)
        ))
        , repeat=2)


circle_05 = EllipseParameters(Coordinate(x=0.0, y=0.0), major_curve=1.0 / 0.5, minor_radius=0.5, angle=0.0)


@pytest.mark.cairo
@approve_image
def test_background_full_border_shadow_in():
    return cairo_widget_test(
        widget=CairoEllipticBackground(
            arc=Arc(ellipse=circle_05, start=Angle.zero(), length=Angle.fullcircle()),
            colour=BLACK.alpha(0.6),
            border=Border(width=0.005, depth=0.005, shadow=ShadowMode.ShadowIn, colour=Colour(0, 0, 0, 0.6))
        )
    )


@pytest.mark.cairo
@approve_image
def test_background_full_border_none():
    return cairo_widget_test(
        widget=CairoEllipticBackground(
            arc=Arc(ellipse=circle_05, start=Angle.zero(), length=Angle.fullcircle()),
            colour=WHITE
        )
    )


@pytest.mark.cairo
@approve_image
def test_background_sector_top_border_none():
    return cairo_widget_test(
        widget=CairoEllipticBackground(
            arc=Arc(
                ellipse=EllipseParameters(
                    Coordinate(x=0.0, y=0.0),
                    major_curve=1.6393,
                    minor_radius=0.5,
                    angle=0.0
                ),
                start=Angle(radians=3.7525),
                length=Angle(radians=1.9199)
            ),
            colour=WHITE
        )
    )
