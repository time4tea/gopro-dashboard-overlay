import itertools
import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from gopro_overlay.framemeta import View, Window
from gopro_overlay.point import Coordinate
from gopro_overlay.timeunits import timeunits
from gopro_overlay.widgets.widgets import Translate, Composite
from gopro_overlay.widgets.widgets_chart import SimpleChart
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
        Translate(
            at=Coordinate(50, 50),
            widget=SimpleChart(value=lambda: view, filled=True, font=font)
        )
    ])


@approve_image
def test_render_chart():
    # Avg: 0.00019, Rate: 5,325.79
    window = Window(
        ts,
        duration=timeunits(minutes=2),
        samples=256,
        key=lambda e: e.alt.magnitude,
    )

    view = window.view(ts.min)

    return time_rendering(
        name="Simple Chart with view",
        dimensions=Dimension(x=800, y=400),
        widgets=[
            Translate(
                at=Coordinate(0, 0),
                widget=Composite(
                    Translate(
                        at=Coordinate(0, 0),
                        widget=SimpleChart(
                            lambda: view,
                            filled=True,
                            font=font
                        )
                    ),
                    Translate(
                        at=Coordinate(0, 100),
                        widget=SimpleChart(
                            lambda: view,
                            filled=False,
                            font=font
                        )
                    ),
                    Translate(
                        at=Coordinate(0, 200),
                        widget=SimpleChart(
                            lambda: view,
                            filled=True,
                            font=font,
                            fill=(0, 255, 0)
                        )
                    )
                )
            ),
            Translate(
                at=Coordinate(350, 0),
                widget=Composite(
                    Translate(
                        at=Coordinate(0, 0),
                        widget=SimpleChart(
                            lambda: view,
                            filled=True,
                            font=font,
                            line=(255, 255, 0)
                        )
                    ),
                    Translate(
                        at=Coordinate(0, 100),
                        widget=SimpleChart(
                            lambda: view,
                            filled=True,
                            font=font,
                            bg=(0, 0, 0),
                            alpha=100,
                        )
                    ),
                    Translate(
                        at=Coordinate(0, 200),
                        widget=SimpleChart(
                            lambda: view,
                            filled=True,
                            font=font,
                            height=100,
                            fill=(0, 255, 0),
                            text=(0, 255, 255)
                        )
                    )
                )
            ),
        ])


@approve_image
def test_render_chart_with_no_data():
    window = Window(
        ts,
        duration=timeunits(minutes=2),
        samples=256,
        key=lambda e: e.bob.magnitude if e.bob else 0
    )

    view = window.view(ts.min)

    return time_rendering(name="Simple Chart with no valid data", widgets=[
        Translate(
            at=Coordinate(50, 50),
            widget=SimpleChart(lambda: view, filled=True, font=font)
        )
    ])


# start = 0.04 / 24.52
@approve_image
def test_render_moving_chart():
    window = Window(
        ts,
        duration=timeunits(minutes=2),
        samples=256,
        key=lambda e: e.alt.magnitude,
        missing=0
    )

    stepper = iter(ts.stepper(timeunits(seconds=1)).steps())

    def get_view():
        return window.view(next(stepper))

    return time_rendering(name="Moving Chart", repeat=50, widgets=[
        Translate(
            at=Coordinate(50, 50),
            widget=SimpleChart(get_view, filled=True, font=font)
        )
    ])
