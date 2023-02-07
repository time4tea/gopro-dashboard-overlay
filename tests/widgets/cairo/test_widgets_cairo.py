from gopro_overlay.dimensions import Dimension
from gopro_overlay.widgets.cairo.cairo import CairoAdapter
from tests.widgets.test_widgets import time_rendering


def cairo_widget_test(widget, repeat=1):
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            CairoAdapter(
                size=Dimension(500, 500),
                widget=widget
            )
        ],
        repeat=repeat
    )
