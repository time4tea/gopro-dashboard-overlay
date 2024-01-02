import pytest

from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.gauge_donut import CairoGaugeDonutAnnotated
from gopro_overlay.widgets.cairo.reading import Reading
from tests.approval import approve_image
from tests.widgets.cairo.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_gauge_donut_defaults():
    return cairo_widget_test(
        widget=CairoGaugeDonutAnnotated(
            reading=lambda: Reading(3.0 / 5)
        ),
        repeat=10
    )


@pytest.mark.cairo
@approve_image
def test_gauge_donut_rotate():
    return cairo_widget_test(
        widget=CairoGaugeDonutAnnotated(
            start=Angle(degrees=343),
            reading=lambda: Reading(3.0 / 5)
        ),
        repeat=10
    )


@pytest.mark.cairo
@approve_image
def test_gauge_donut_reversed():
    return cairo_widget_test(
        widget=CairoGaugeDonutAnnotated(
            length=Angle(degrees=-143),
            reading=lambda: Reading(3.0 / 5)
        ),
        repeat=10
    )

@pytest.mark.cairo
@approve_image
def test_gauge_donut_sector():
    return cairo_widget_test(
        widget=CairoGaugeDonutAnnotated(
            length=Angle(degrees=-143),
            reading=lambda: Reading(3.0 / 5),
            reading_arc_max= lambda: Reading(3.5 / 5),
            reading_arc_min=lambda: Reading(2.5 / 5),
        ),
        repeat=10
    )
