import pytest

from gopro_overlay.dimensions import Dimension
from gopro_overlay.widgets.msi import MotorspeedIndicator, MotorspeedIndicator2
from tests.approval import approve_image
from tests.widgets import test_widgets_setup
from tests.widgets.test_widgets import time_rendering

font = test_widgets_setup.font
ts = test_widgets_setup.ts


@pytest.mark.gfx
@approve_image
def test_gauge():
    size = 256
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(size, size),
        widgets=[
            MotorspeedIndicator(
                size=size, font=font, green=40, yellow=46, end=200,
                needle=1,
                reading=lambda: 125
            )
        ]
    )


@pytest.mark.gfx
@approve_image
def test_gauge_msi_2():
    size = 256
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(size, size),
        widgets=[
            MotorspeedIndicator2(
                size=size, font=font, green=40, yellow=46, end=200,
                reading=lambda: 125
            )
        ]
    )


@pytest.mark.gfx
@approve_image
def test_gauge_rotate_90():
    size = 256
    return time_rendering(
        name="test_gauge_rotate_90",
        dimensions=Dimension(size, size),
        widgets=[
            MotorspeedIndicator(
                size=size, font=font, green=40, yellow=46, end=200,
                needle=1,
                rotate=90,
                reading=lambda: 125
            )
        ]
    )


@pytest.mark.gfx
@approve_image
def test_no_needle():
    size = 256
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(size, size),
        widgets=[
            MotorspeedIndicator(
                size=size, font=font, green=40, yellow=46, end=200,
                needle=0,
                reading=lambda: 125
            )
        ]
    )
