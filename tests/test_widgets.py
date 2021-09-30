import itertools
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.point import Coordinate
from gopro_overlay.timeseries import Window
from gopro_overlay.timing import PoorTimer
from gopro_overlay.widgets import simple_icon, Text, Scene
from gopro_overlay.widgets_info import LeftInfoPanel, RightInfoPanel, BigMetric
from gopro_overlay.widgets_chart import SimpleChart
from tests.testenvironment import is_ci

font = ImageFont.truetype(font="Roboto-Medium.ttf", size=18)
title_font = font.font_variant(size=16)

ts = fake.fake_timeseries(timedelta(minutes=10), step=timedelta(seconds=1))


# don't know why this fails only in PyCharm with AttributeError: module 'importlib' has no attribute 'resources'

def test_render_sample():
    widgets = [
        LeftInfoPanel(Coordinate(600, 600), "mountain.png", lambda: "ALT(m)", lambda: "100m", title_font, font),
        RightInfoPanel(Coordinate(1200, 600), "mountain.png", lambda: "ALT(m)", lambda: "100m", title_font, font),
        simple_icon(Coordinate(300, 300), "gauge-1.png"),
        Text(Coordinate(300, 300), lambda: "Hello", font),
    ]

    draw = Scene(widgets).draw()

    if not is_ci():
        draw.show()


def test_render_text():
    time_rendering("simple text", [Text(Coordinate(300, 300), lambda: "Hello", font)])


def test_render_panel():
    time_rendering("info panel",
                   widgets=[
                       LeftInfoPanel(Coordinate(600, 600), "mountain.png", lambda: "ALT(m)", lambda: "100m", title_font,
                                     font),
                   ]
                   )


def test_render_simple_chart():
    view = list(itertools.chain(
        itertools.repeat(0, 128),
        itertools.repeat(1, 128)
    ))
    time_rendering("Simple Chart", [
        SimpleChart(Coordinate(600, 600), lambda: view, filled=True, font=font)
    ])


def test_render_chart():
    window = Window(ts,
                    duration=timedelta(minutes=2),
                    samples=256,
                    key=lambda e: e.alt.magnitude if e.alt else 0,
                    missing=None)

    view = window.view(ts.min)

    time_rendering(name="Simple Chart with view", widgets=[
        SimpleChart(Coordinate(600, 600), lambda: view, filled=True, font=font)
    ])


def test_render_big_text():
    time_rendering(name="big speed", widgets=[
        BigMetric(Coordinate(600, 600), title=lambda: "MPH", value=lambda: "27", font=font)
    ])


def time_rendering(name, widgets):
    timer = PoorTimer(name)

    scene = Scene(widgets)
    for i in range(0, 100):
        draw = timer.time(lambda: scene.draw())

    if not is_ci():
        draw.show()

    print(timer)
