import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets import Translate
from gopro_overlay.widgets_asi import AirspeedIndicator
from tests.approval import approve_image
from tests.test_widgets import time_rendering

font = ImageFont.truetype(font='Roboto-Medium.ttf', size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_timeseries(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


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
