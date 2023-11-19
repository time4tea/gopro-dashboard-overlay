import pytest

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.colour import RED, Colour, WHITE, BLACK
from gopro_overlay.widgets.cairo.gauge_marker import circle_with_radius
from gopro_overlay.widgets.cairo.gauge_round_254 import CairoGaugeRoundAnnotated
from gopro_overlay.widgets.cairo.gauge_sector_254 import CairoGaugeSectorAnnotated
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.needle_sector import SectorNeedle, SectorArc
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.tick import TickParameters
from tests.approval import approve_image
from tests.widgets.cairo.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_gauge_sector_254_defaults():
    return cairo_widget_test(
        widget=CairoGaugeSectorAnnotated(
            v_max=60,
            sectors=12,
            reading=lambda: Reading(23.0 / 60),
            arc_inner_colour=Colour.hex("4E53E9").alpha(0.2),
            arc_outer_colour=Colour.hex("4E53E9").alpha(0.8),
            reading_arc_max=lambda: Reading(20.0 / 60)
        ),
        repeat=10
    )



@pytest.mark.cairo
@approve_image
def test_gauge_sector_needle():
    centre = Coordinate(x=0.0, y=0.0)
    return cairo_widget_test(
        widget=SectorNeedle(
            inner=circle_with_radius(0.20, centre),
            outer=circle_with_radius(0.49, centre),
            lines=[LineParameters(3.0 / 400, colour=WHITE)],
            start=Angle(degrees=143),
            length=Angle(degrees=254),
            reading=lambda: Reading(3.0 / 17),

        ),
        repeat=10
    )

@pytest.mark.cairo
@approve_image
def test_gauge_sector_arc():
    return cairo_widget_test(
        widget=SectorArc(
            inner=0.30,
            outer=0.49,
            inner_colour=Colour.hex("4E53E9").alpha(0.2),
            outer_colour=Colour.hex("4E53E9").alpha(0.8),
            start=Angle(degrees=143),
            length=Angle(degrees=254),
            reading_max=lambda: Reading(12.0 / 17)
        ),
        repeat=10
    )



