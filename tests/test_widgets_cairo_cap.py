import pytest

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.cap import Cap
from gopro_overlay.widgets.cairo.colour import Colour
from tests.approval import approve_image
from tests.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
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
