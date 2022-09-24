import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from gopro_overlay.widgets.bar import Bar
from tests.approval import approve_image
from tests.test_widgets import time_rendering

font = ImageFont.truetype(font='Roboto-Medium.ttf', size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


@approve_image
def test_gauge():
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 75),
        widgets=[
            Bar(
                size=Dimension(400, 30),
                reading=lambda: 9
            )
        ]
    )


@approve_image
def test_gauge_negative():
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 75),
        widgets=[
            Bar(
                size=Dimension(400, 30),
                reading=lambda: -9
            )
        ]
    )
