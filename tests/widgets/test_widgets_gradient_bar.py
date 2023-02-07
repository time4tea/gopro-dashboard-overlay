import pytest

from gopro_overlay.dimensions import Dimension
from gopro_overlay.widgets.gradient_bar import GradientBar
from gopro_overlay.widgets.widgets import Widget
from tests.widgets import test_widgets_setup
from tests.approval import approve_image
from tests.widgets.test_widgets import time_rendering

font = test_widgets_setup.font
ts = test_widgets_setup.ts


def do_bar(bar: Widget):
    return time_rendering(name="test_power_zones", dimensions=Dimension(500, 75), widgets=[bar])


@pytest.mark.gfx
@approve_image
def test_gauge_over_max():
    return do_bar(GradientBar(size=Dimension(400, 30), max_value=400, reading=lambda: 500,))

@pytest.mark.gfx
@approve_image
def test_gauge_at_max():
    return do_bar(GradientBar(size=Dimension(400, 30), max_value=400, reading=lambda: 400,))

@pytest.mark.gfx
@approve_image
def test_gauge_lower():
    return do_bar(GradientBar(size=Dimension(400, 30), max_value=400, reading=lambda: 100,))

@pytest.mark.gfx
@approve_image
def test_gauge_med():
    return do_bar(GradientBar(size=Dimension(400, 50), cr=30, max_value=300, reading=lambda: 200,))
