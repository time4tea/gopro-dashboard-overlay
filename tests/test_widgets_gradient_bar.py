import pytest

from gopro_overlay.dimensions import Dimension
from gopro_overlay.widgets.gradient_bar import GradientBar
from tests import test_widgets_setup
from tests.approval import approve_image
from tests.test_widgets import time_rendering

font = test_widgets_setup.font
ts = test_widgets_setup.ts


@pytest.mark.gfx
@approve_image
def test_gauge():
    return time_rendering(
        name="test_power_zones",
        dimensions=Dimension(500, 75),
        widgets=[
            GradientBar(
            size=Dimension(400, 30),
            reading=lambda: 250,            
        )
        ]
    )


# @pytest.mark.gfx
# @approve_image
# def test_gauge_negative():
#     return time_rendering(
#         name="test_gauge",
#         dimensions=Dimension(500, 75),
#         widgets=[
#             Bar(
#                 size=Dimension(400, 30),
#                 reading=lambda: -9
#             )
#         ]
#     )
