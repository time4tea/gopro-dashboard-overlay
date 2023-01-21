import pytest

from gopro_overlay.dimensions import Dimension
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.asi import AirspeedIndicator
from gopro_overlay.widgets.widgets import Translate
from tests import test_widgets_setup
from tests.approval import approve_image
from tests.test_widgets import time_rendering

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
            AirspeedIndicator(
                size=size, font=font, Vs0=40, Vs=46, Vfe=84, Vno=130, Vne=200,
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
            AirspeedIndicator(
                size=size, font=font, Vs0=40, Vs=46, Vfe=84, Vno=130, Vne=200, rotate=90,
                reading=lambda: 125
            )
        ]
    )


@pytest.mark.gfx
@approve_image
def test_gauge_rotate_180():
    size = 256
    return time_rendering(
        name="test_gauge_rotate_180",
        dimensions=Dimension(size, size),
        widgets=[
            AirspeedIndicator(
                size=size, font=font, Vs0=40, Vs=46, Vfe=84, Vno=130, Vne=200, rotate=180,
                reading=lambda: 125
            )
        ]
    )


@pytest.mark.gfx
@approve_image
def test_gauge_below_min():
    size = 256
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(size, size),
        widgets=[
            AirspeedIndicator(
                size=size, font=font, Vs0=40, Vs=46, Vfe=84, Vno=130, Vne=200,
                reading=lambda: 0
            )
        ]
    )


@pytest.mark.gfx
@approve_image
def test_gauge_smaller_values():
    size = 256
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(size, size),
        widgets=[
            AirspeedIndicator(
                size=size, font=font, Vs0=0, Vs=10, Vfe=20, Vno=35, Vne=40,
                reading=lambda: 25
            )
        ]
    )


@pytest.mark.gfx
@approve_image
def test_gauge_translated():
    size = 256
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(size, size),
        widgets=[
            Translate(
                at=Coordinate(10, 10),
                widget=AirspeedIndicator(
                    size=size, font=font, Vs0=40, Vs=46, Vfe=84, Vno=130, Vne=200,
                    reading=lambda: 125
                )
            )
        ]
    )
