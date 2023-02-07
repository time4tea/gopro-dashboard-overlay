import pytest

from gopro_overlay.dimensions import Dimension
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.compass_arrow import CompassArrow
from gopro_overlay.widgets.widgets import Composite, Translate
from tests.widgets import test_widgets_setup
from tests.approval import approve_image
from tests.widgets.test_widgets import time_rendering

font = test_widgets_setup.font
ts = test_widgets_setup.ts


@pytest.mark.gfx
@approve_image
def test_compass_med():
    return time_rendering(
        name="test_compass_med",
        dimensions=Dimension(250, 250),
        widgets=[
            CompassArrow(
                size=250,
                reading=lambda: 45,
                bg=(117, 175, 255),
                font=font,
            ),
        ])


@pytest.mark.gfx
@approve_image
def test_compass_small():
    return time_rendering(
        name="test_compass_small",
        dimensions=Dimension(250, 250),
        widgets=[
            Translate(
                Coordinate(10, 10),
                Composite(CompassArrow(
                    size=100,
                    reading=lambda: 20,
                    font=font,
                    text=(255, 255, 0),
                    bg=(0, 255, 255),
                    arrow=(0, 0, 0)
                ), )
            )
        ])


@pytest.mark.gfx
@approve_image
def test_compass_big():
    return time_rendering(
        name="test_compass_big",
        dimensions=Dimension(400, 400),
        widgets=[
            Translate(
                Coordinate(0, 0),
                Composite(CompassArrow(size=400,
                                       reading=lambda: 90,
                                       font=font.font_variant(size=48),
                                       text=(255, 255, 255),
                                       # bg=(0, 255, 255),
                                       arrow=(255, 0, 255),
                                       outline=(255, 255, 255, 0)
                                       ),
                          )
            )
        ])
