import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from tests.approval import approve_image
from tests.test_widgets import time_rendering

font = ImageFont.truetype(font='Roboto-Medium.ttf', size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


class Bar:

    def __init__(self, size, reading):
        self.reading = reading
        self.size = size
        self.corner_radius = 5
        self.outline = (255, 255, 255)
        self.line_width = 3
        self.min_value = -10
        self.max_value = 10

    def x_coord(self, value):
        value = max(min(value, self.max_value), self.min_value)
        range = self.max_value - self.min_value
        scale = (self.size.x - (self.line_width + 2)) / range
        shifted = value - self.min_value
        return shifted * scale

    def draw(self, image, draw):
        current = self.reading()
        draw.rounded_rectangle(
            ((0, 0), (self.size.x - 1, self.size.y - 1)),
            radius=self.corner_radius,
            outline=self.outline,
            width=self.line_width,
        )
        draw.line(
            ((self.x_coord(0), 0), (self.x_coord(0), self.size.y)),
            fill=(255, 255, 255)
        )
        draw.rectangle(
            ((self.x_coord(current), self.line_width + 1), (self.x_coord(0), self.size.y - (self.line_width + 2))),
            fill=(255, 255, 255)
        )
        draw.rectangle(
            ((self.x_coord(current * 0.95), self.line_width + 1),
             (self.x_coord(current), self.size.y - (self.line_width + 2))),
            fill=(0, 255, 0)
        )


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
