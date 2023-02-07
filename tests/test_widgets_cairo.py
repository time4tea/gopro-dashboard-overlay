from gopro_overlay.dimensions import Dimension
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.cairo import CairoAdapter, CairoTranslate
from tests.test_widgets import time_rendering


def cairo_widget_test(widget, repeat=1):
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            CairoAdapter(
                size=Dimension(500, 500),
                widget=CairoTranslate(by=Coordinate(-0.5, -0.5), widget=widget)
            )
        ],
        repeat=repeat
    )
