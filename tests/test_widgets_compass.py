import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets import Composite, Translate, Text
from gopro_overlay.widgets_compass import Compass
from tests.approval import approve_image
from tests.test_widgets import time_rendering

font = ImageFont.truetype(font='Roboto-Medium.ttf', size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_timeseries(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


@approve_image
def test_compass_med():
    return time_rendering(
        name="viewport",
        dimensions=Dimension(250, 250),
        widgets=[
            Text(at=Coordinate(100, 150), value=lambda: "Partially Visible", font=font.font_variant(size=64)),
            Translate(
                Coordinate(10, 10),
                Composite(
                    Compass(
                        size=200,
                        reading=lambda: 45,
                        font=font,
                    ),
                )
            )
        ])


@approve_image
def test_compass_small():
    return time_rendering(
        name="viewport",
        dimensions=Dimension(250, 250),
        widgets=[
            Translate(
                Coordinate(10, 10),
                Composite(Compass(
                    size=100,
                    reading=lambda: 20,
                    font=font,
                    colour=(255, 255, 0),
                    bg=(0, 255, 255),
                    fg=(0, 0, 0)
                ), )
            )
        ])


@approve_image
def test_compass_big():
    return time_rendering(
        name="viewport",
        dimensions=Dimension(400, 400),
        widgets=[
            Translate(
                Coordinate(0, 0),
                Composite(Compass(size=400,
                                  reading=lambda: 20,
                                  font=font.font_variant(size=48),
                                  colour=(255, 255, 255),
                                  bg=(0, 255, 255),
                                  fg=(255, 0, 255)
                                  ),
                          )
            )
        ])
