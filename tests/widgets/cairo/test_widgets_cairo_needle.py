import pytest

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.colour import RED
from gopro_overlay.widgets.cairo.needle import Needle, NeedleParameter
from gopro_overlay.widgets.cairo.reading import Reading
from tests.approval import approve_image
from tests.widgets.cairo.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_needle():
    return cairo_widget_test(
        widget=Needle(
            reading=lambda: Reading(0.65),
            centre=Coordinate(0.5, 0.5),
            start=Angle(degrees=143),
            length=Angle(degrees=254),
            tip=NeedleParameter(width=0.0175, length=0.46),
            rear=NeedleParameter(width=0.03, length=0.135),
            colour=RED
        )
    )
