import itertools
import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake, layout
from gopro_overlay.point import Coordinate
from gopro_overlay.timeseries import Window, View
from gopro_overlay.timing import PoorTimer
from gopro_overlay.units import units
from gopro_overlay.widgets import simple_icon, Text, Scene, CachingText
from gopro_overlay.widgets_chart import SimpleChart
from gopro_overlay.widgets_info import LeftInfoPanel, BigMetric, ComparativeEnergy
from tests.approval import approve_image
from tests.testenvironment import is_ci

font = ImageFont.truetype(font="Roboto-Medium.ttf", size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_timeseries(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


@approve_image
def test_render_icon():
    return time_rendering("icon", widgets=[
        simple_icon(Coordinate(50, 50), "gauge-1.png"),
    ])


@approve_image
def test_render_text():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font)])


@approve_image
def test_render_caching_text_small():
    return time_rendering("simple text (cached)", [CachingText(Coordinate(50, 50), lambda: "Hello", font)])


@approve_image
def test_render_text_big():
    # 15ms target to beat
    return time_rendering("big text",
                          [Text(Coordinate(50, 50), lambda: "Hello", font.font_variant(size=160))])


@approve_image
def test_render_caching_text_big():
    # Avg: 0.00014, Rate: 6,966.58
    return time_rendering("big text (cached)",
                          [CachingText(Coordinate(50, 50), lambda: "Hello", font.font_variant(size=160))])


@approve_image
def test_render_panel():
    return time_rendering("info panel",
                          widgets=[
                              LeftInfoPanel(Coordinate(10, 10), "mountain.png", lambda: "ALT(m)", lambda: "100m",
                                            title_font, font)
                          ])


@approve_image
def test_render_gps_info():
    # Avg: 0.00645, Rate: 155.05
    entry = ts.get(ts.min)
    return time_rendering(name="gps info", widgets=layout.gps_info(Coordinate(400, 10), lambda: entry, font))


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
    window = Window(ts,
                    duration=timedelta(minutes=2),
                    samples=256,
                    key=lambda e: e.alt.magnitude if e.alt else 0,
                    missing=None)

    view = window.view(ts.min)

    return time_rendering(name="Simple Chart with view", widgets=[
        SimpleChart(Coordinate(50, 50), lambda: view, filled=True, font=font)
    ])


# start = 0.04 / 24.52
def test_render_moving_chart():
    window = Window(ts,
                    duration=timedelta(minutes=2),
                    samples=256,
                    key=lambda e: e.alt.magnitude if e.alt else 0,
                    missing=None)

    stepper = iter(ts.stepper(timedelta(seconds=1)).steps())

    def get_view():
        return window.view(next(stepper))

    return time_rendering(name="Moving Chart", repeat=50, widgets=[
        SimpleChart(Coordinate(50, 50), get_view, filled=True, font=font)
    ])


@approve_image
def test_render_big_metric():
    # Avg: 0.00026, Rate: 3,871.63
    return time_rendering(name="big speed", widgets=[
        BigMetric(Coordinate(10, 10), title=lambda: "MPH", value=lambda: "27", font=font)
    ])


@approve_image
def test_render_comparative_energy():
    # Avg: 0.00148, Rate: 676.70
    speed = units.Quantity(25, units.mph)

    return time_rendering(name="comparative energy",
                          dimensions=(1300, 200),
                          widgets=[
                              ComparativeEnergy(Coordinate(10, 50),
                                                font=font,
                                                speed=lambda: speed,
                                                person=units.Quantity(60, units.kg),
                                                bike=units.Quantity(12, units.kg),
                                                car=units.Quantity(2678, units.kg),
                                                van=units.Quantity(3500, units.kg)
                                                )
                          ])


def time_rendering(name, widgets, dimensions=None, repeat=100):
    dimensions = dimensions or (600, 300)
    timer = PoorTimer(name)

    scene = Scene(widgets, dimensions=dimensions)
    for i in range(0, repeat):
        draw = timer.time(lambda: scene.draw())

    if not is_ci():
        draw.show()

    print(timer)
    return draw
