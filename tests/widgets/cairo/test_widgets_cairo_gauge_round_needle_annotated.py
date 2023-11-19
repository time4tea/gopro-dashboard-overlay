import pytest

from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.colour import RED, Colour, WHITE, BLACK
from gopro_overlay.widgets.cairo.gauge_round_254 import CairoGaugeRoundAnnotated
from gopro_overlay.widgets.cairo.reading import Reading
from tests.approval import approve_image
from tests.widgets.cairo.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_gauge_round_254_defaults():
    return cairo_widget_test(
        widget=CairoGaugeRoundAnnotated(
            reading=lambda: Reading(3.0 / 17)
        ),
        repeat=10
    )


@pytest.mark.cairo
@approve_image
def test_gauge_round_254_alt():
    return cairo_widget_test(
        widget=CairoGaugeRoundAnnotated(
            reading=lambda: Reading(3.0 / 17),
            v_max=60,
            sectors=12,
            background_colour=BLACK.alpha(0.6),
            major_annotation_colour=WHITE,
            minor_annotation_colour=WHITE,
            major_tick_colour=WHITE,
            minor_tick_colour=WHITE,
        ),
        repeat=10
    )


@pytest.mark.cairo
@approve_image
def test_gauge_round_254_slower_speeds():
    return cairo_widget_test(
        widget=CairoGaugeRoundAnnotated(
            start=Angle(degrees=90),
            length=Angle(degrees=270),
            v_max=40,
            sectors=8,
            minor_annotation_colour=RED,
            major_annotation_colour=Colour(0,1,0),
            background_colour=Colour(0,0,1,0.6),
            needle_colour=WHITE,
            reading=lambda: Reading(3.0 / 17)
        ),
        repeat=10
    )


