import contextlib
import math

import cairo
import pytest
from PIL import Image, ImageDraw, ImageFilter

from gopro_overlay.dimensions import Dimension
from gopro_overlay.widgets.cairo.cairo import CairoWidget, saved, CairoAdapter
from gopro_overlay.widgets.cairo.colour import Colour
from gopro_overlay.widgets.cairo.ellipse import EllipseParameters
from gopro_overlay.widgets.cairo.gauge import CairoGauge270, circle_with_radius, CairoEllipseMarker
from gopro_overlay.widgets.cairo.line import LineParameters
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.scale import CairoScale
from gopro_overlay.widgets.cairo.tick import TickParameters
from gopro_overlay.widgets.widgets import Widget
from tests import test_widgets_setup
from tests.approval import approve_image
from tests.test_widgets import time_rendering
from tests.test_widgets_circuit import cairo_widget_test

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


@pytest.mark.gfx
@approve_image
def test_cairo_simple_scale():
    return cairo_widget_test(CairoScale(
        outer=circle_with_radius(0.45),
        inner=circle_with_radius(0.40),
        tick=TickParameters(math.radians(45)),
        lines=[
            LineParameters(0.02, Colour(1.0, 1.0, 1.0), cap=cairo.LINE_CAP_SQUARE)
        ],
        start=math.pi / 2,
        length=math.pi * 3 / 2
    ))


class EffectsWidget(Widget):
    def __init__(self, size: Dimension, widget: Widget):
        self.dimensions = size
        self.widget = widget

    def draw(self, image: Image, draw: ImageDraw):
        rect = Image.new('RGBA', (self.dimensions.x, self.dimensions.y), (0, 0, 0, 0))
        rect_draw = ImageDraw.Draw(rect)

        self.widget.draw(rect, rect_draw)

        image.alpha_composite(rect.filter(ImageFilter.BoxBlur(radius=2)), (0, 0))


def test_something():
    size = Dimension(500, 500)
    time_rendering(
        "blur",
        widgets=[
            EffectsWidget(size, CairoAdapter(size, CairoGauge270(reading=lambda: Reading(0.600)))),
        ],
        dimensions=size,
        repeat=50
    )


@pytest.mark.gfx
@approve_image
def test_cairo_gauge_270():
    return cairo_widget_test(
        CairoGauge270(reading=lambda: Reading(1.000))
    )


@pytest.mark.gfx
@approve_image
def test_cairo_ellipse_marker():
    return cairo_widget_test(
        CairoEllipseMarker(
            ellipse=circle_with_radius(0.45),
            outer=LineParameters(width=0.01),
            inner=LineParameters(width=0.01, colour=Colour.hex("00BFFF")),
            reading=lambda: Reading(1.000),
            start=math.pi / 2,
            length=math.pi * 3 / 2
        )
    )
