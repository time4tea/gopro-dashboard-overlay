import pytest

from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.gauge_round_254 import GaugeRoundNeedleAnnotated
from gopro_overlay.widgets.cairo.reading import Reading
from tests.approval import approve_image
from tests.widgets.cairo.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_gauge_round_254_defaults():
    return cairo_widget_test(
        widget=GaugeRoundNeedleAnnotated(
            reading=lambda: Reading(3.0 / 17)
        ),
        repeat=10
    )


@pytest.mark.cairo
@approve_image
def test_gauge_round_254_slower_speeds():
    return cairo_widget_test(
        widget=GaugeRoundNeedleAnnotated(
            start=Angle(degrees=90),
            length=Angle(degrees=270),
            v_max=40,
            sectors=8,
            reading=lambda: Reading(3.0 / 17)
        ),
        repeat=10
    )


