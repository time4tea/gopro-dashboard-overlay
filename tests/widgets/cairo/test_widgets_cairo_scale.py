import pytest

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.cairo import CairoComposite
from gopro_overlay.widgets.cairo.colour import BLACK
from gopro_overlay.widgets.cairo.ellipse import EllipseParameters
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.scale import CairoScale
from gopro_overlay.widgets.cairo.tick import TickParameters
from tests.approval import approve_image
from tests.widgets.cairo.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_scale():
    start = Angle(degrees=143)
    length = Angle(degrees=254)
    step = Angle.fullcircle() / 12

    return cairo_widget_test(
        widget=CairoComposite(
            widgets=[
                CairoScale(
                    inner=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.43, minor_radius=0.43, angle=0.0),
                    outer=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.49, minor_radius=0.49, angle=0.0),
                    tick=TickParameters(step=step, first=1),
                    length=length,
                    start=start,
                    lines=[LineParameters(
                        width=6.0 / 400.0,
                        colour=BLACK
                    )]
                ),
                CairoScale(
                    inner=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.46, minor_radius=0.46, angle=0.0),
                    outer=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.49, minor_radius=0.49, angle=0.0),
                    tick=TickParameters(step=step / 2.0, first=0, skipped=3),
                    length=length,
                    start=start,
                    lines=[LineParameters(
                        width=1.0 / 400.0,
                        colour=BLACK
                    )]
                ),
            ]
        )
    )
