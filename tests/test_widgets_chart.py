import itertools
import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.framemeta import View, Window
from gopro_overlay.point import Coordinate
from gopro_overlay.timeunits import timeunits
from gopro_overlay.widgets_chart import SimpleChart
from tests.approval import approve_image
from tests.test_widgets import time_rendering

font = ImageFont.truetype(font='Roboto-Medium.ttf', size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


@approve_image
def test_render_simple_chart():
    # Avg: 0.00018, Rate: 5,491.91
    view = View(data=list(itertools.chain(
        itertools.repeat(0, 128),
        itertools.repeat(1, 128)
    )), version=1)
    return time_rendering("Simple Chart", [
        SimpleChart(Coordinate(50, 50), lambda: view, filled=True, font=font)
    ])


@approve_image
def test_render_chart():
    # Avg: 0.00019, Rate: 5,325.79
    window = Window(
        ts,
        duration=timeunits(minutes=2),
        samples=256,
        key=lambda e: e.alt,
        fmt=lambda v: v.magnitude
    )

    view = window.view(ts.min)

    return time_rendering(name="Simple Chart with view", widgets=[
        SimpleChart(Coordinate(50, 50), lambda: view, filled=True, font=font)
    ])


@approve_image
def test_render_chart_with_no_data():
    window = Window(
        ts,
        duration=timeunits(minutes=2),
        samples=256,
        key=lambda e: e.bob, fmt=lambda v: v.magnitude
    )

    view = window.view(ts.min)

    return time_rendering(name="Simple Chart with no valid data", widgets=[
        SimpleChart(Coordinate(50, 50), lambda: view, filled=True, font=font)
    ])


# start = 0.04 / 24.52
@approve_image
def test_render_moving_chart():
    window = Window(
        ts,
        duration=timeunits(minutes=2),
        samples=256,
        key=lambda e: e.alt,
        fmt=lambda v: v.magnitude,
        missing=0
    )

    stepper = iter(ts.stepper(timeunits(seconds=1)).steps())

    def get_view():
        return window.view(next(stepper))

    return time_rendering(name="Moving Chart", repeat=50, widgets=[
        SimpleChart(Coordinate(50, 50), get_view, filled=True, font=font)
    ])
