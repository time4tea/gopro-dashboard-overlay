import pytest

from gopro_overlay.widgets.cairo.gauge_round_254 import GaugeRound254
from tests.approval import approve_image
from tests.widgets.cairo.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_gauge_round_254():
    return cairo_widget_test(widget=GaugeRound254(), repeat=1)
