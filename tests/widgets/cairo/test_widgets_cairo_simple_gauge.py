import contextlib
import math

import cairo
import pytest

from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.colour import Colour
from gopro_overlay.widgets.cairo.gauge_marker import CairoGaugeMarker, circle_with_radius, CairoEllipseMarker, MarkerCircle
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.scale import CairoScale
from gopro_overlay.widgets.cairo.tick import TickParameters
from tests.widgets import test_widgets_setup
from tests.approval import approve_image
from tests.widgets.test_widgets_circuit import cairo_widget_test

ts = test_widgets_setup.ts


def pt():
    return ts.get(ts.min).point


cos45 = math.sqrt(2.0) * 0.5


class Gradient:

    @contextlib.contextmanager
    def applied_to(self, context: cairo.Context):
        pattern = cairo.LinearGradient(-cos45, -cos45, cos45, cos45)
        pattern.add_color_stop_rgba(0.0, *Colour(255, 0, 0).rgba())
        pattern.add_color_stop_rgba(1.0, *Colour(0, 255, 0).rgba())
        context.set_source(pattern)
        yield


@pytest.mark.cairo
@approve_image
def test_cairo_simple_scale():
    return cairo_widget_test(CairoScale(
        outer=circle_with_radius(0.45),
        inner=circle_with_radius(0.40),
        tick=TickParameters(step=Angle(degrees=45)),
        lines=[
            LineParameters(0.02, Colour(1.0, 1.0, 1.0), cap=cairo.LINE_CAP_SQUARE)
        ],
        start=Angle(degrees=90),
        length=Angle(degrees=270)
    ))


@pytest.mark.cairo
@approve_image
def test_cairo_gauge_marker():
    return cairo_widget_test(
        CairoGaugeMarker(
            reading=lambda: Reading(1.000)
        )
    )


@pytest.mark.cairo
@approve_image
def test_cairo_ellipse_marker():
    return cairo_widget_test(
        CairoEllipseMarker(
            ellipse=circle_with_radius(0.45),
            reading=lambda: Reading(1.000),
            start=Angle(degrees=90),
            length=Angle(degrees=270),
            marker=MarkerCircle(
                outer=LineParameters(width=0.01),
                inner=LineParameters(width=0.01, colour=Colour.hex("00BFFF")),
            )
        ),
    )
