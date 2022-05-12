import itertools
import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from gopro_overlay.framemeta import View, Window
from gopro_overlay.layout import BigMetric, gps_info
from gopro_overlay.layout_components import text, metric
from gopro_overlay.point import Coordinate
from gopro_overlay.timeunits import timeunits
from gopro_overlay.timing import PoorTimer
from gopro_overlay.units import units
from gopro_overlay.widgets import simple_icon, Text, Scene, CachingText, Composite, Translate, Frame
from gopro_overlay.widgets_chart import SimpleChart
from gopro_overlay.widgets_info import ComparativeEnergy
from tests.approval import approve_image
from tests.testenvironment import is_make

font = ImageFont.truetype(font='Roboto-Medium.ttf', size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


@approve_image
def test_render_icon():
    return time_rendering("icon", widgets=[
        simple_icon(Coordinate(50, 50), "gauge-1.png", invert=True),
    ])


@approve_image
def test_render_text():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font)])


@approve_image
def test_render_text_colour():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font, fill=(255, 255, 0))])


@approve_image
def test_render_text_vertical():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font, direction="ttb", align="lt")])


@approve_image
def test_render_caching_text_vertical():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font, direction="ttb", align="lt")])


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
def test_render_gps_info():
    # Avg: 0.00645, Rate: 155.05
    entry = ts.get(ts.min)
    return time_rendering(
        name="gps info",
        widgets=[gps_info(Coordinate(400, 10), lambda: entry, font)]
    )


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
                    duration=timeunits(minutes=2),
                    samples=256,
                    key=lambda e: e.alt, fmt=lambda v: v.magnitude)

    view = window.view(ts.min)

    return time_rendering(name="Simple Chart with view", widgets=[
        SimpleChart(Coordinate(50, 50), lambda: view, filled=True, font=font)
    ])


def test_render_chart_with_no_data():
    window = Window(ts,
                    duration=timeunits(minutes=2),
                    samples=256,
                    key=lambda e: e.bob, fmt=lambda v: v.magnitude)

    view = window.view(ts.min)

    return time_rendering(name="Simple Chart with no valid data", widgets=[
        SimpleChart(Coordinate(50, 50), lambda: view, filled=True, font=font)
    ])


# start = 0.04 / 24.52
def test_render_moving_chart():
    window = Window(ts,
                    duration=timeunits(minutes=2),
                    samples=256,
                    key=lambda e: e.alt.magnitude if e.alt else 0,
                    missing=None)

    stepper = iter(ts.stepper(timeunits(seconds=1)).steps())

    def get_view():
        return window.view(next(stepper))

    return time_rendering(name="Moving Chart", repeat=50, widgets=[
        SimpleChart(Coordinate(50, 50), get_view, filled=True, font=font)
    ])


@approve_image
def test_render_big_metric():
    # Avg: 0.00026, Rate: 3,871.63
    return time_rendering(name="big speed", widgets=[
        BigMetric(Coordinate(10, 10), title=lambda: "MPH", value=lambda: "27", font_title=font,
                  font_metric=font.font_variant(size=160))
    ])


@approve_image
def test_render_comparative_energy():
    # Avg: 0.00148, Rate: 676.70
    speed = units.Quantity(25, units.mph)

    return time_rendering(name="comparative energy",
                          dimensions=Dimension(x=1300, y=200),
                          widgets=[
                              Translate(
                                  Coordinate(10, 50),
                                  ComparativeEnergy(
                                      font=font,
                                      speed=lambda: speed,
                                      person=units.Quantity(60, units.kg),
                                      bike=units.Quantity(12, units.kg),
                                      car=units.Quantity(2678, units.kg),
                                      van=units.Quantity(3500, units.kg)
                                  )
                              )
                          ])


@approve_image
def test_text_component():
    return time_rendering(name="text", widgets=[
        text(at=Coordinate(100, 100), value=lambda: "String", font=font.font_variant(size=50))
    ])


@approve_image
def test_metric_component():
    return time_rendering(name="text", widgets=[
        metric(
            at=Coordinate(100, 100),
            entry=lambda: ts.get(ts.min),
            accessor=lambda e: e.speed,
            formatter=lambda v: format(v, ".1f"),
            font=font.font_variant(size=160),
        )
    ])


@approve_image
def test_composite_viewport():
    return time_rendering(name="viewport", widgets=[
        Translate(
            Coordinate(330, 130),
            Composite(
                text(at=Coordinate(0, 0), cache=True, value=lambda: "String", font=font.font_variant(size=50)),
                simple_icon(Coordinate(0, 50), "gauge-1.png", invert=True),
            )
        )
    ])


@approve_image
def test_frame_border_visible_over_content():
    return time_rendering(name="viewport", widgets=[
        Translate(
            Coordinate(10, 10),
            Frame(
                dimensions=Dimension(300, 200),
                opacity=0.6,
                fill=(0, 0, 0),
                outline=(255, 255, 255),
                child=CachingText(
                    at=Coordinate(-8, 0),
                    fill=(255, 255, 0),
                    value=lambda: "Hello",
                    font=font.font_variant(size=64)
                ),
            )
        )
    ])


@approve_image
def test_frame_circular():
    return time_rendering(name="viewport", widgets=[
        Composite(
            Text(at=Coordinate(100, 150), value=lambda: "Partially Visible", font=font.font_variant(size=64)),
            Translate(
                Coordinate(100, 00),
                Frame(
                    dimensions=Dimension(200, 200),
                    opacity=0.6,
                    fill=(0, 0, 0),
                    outline=(255, 255, 255),
                    corner_radius=100,
                    child=CachingText(
                        at=Coordinate(0, 000),
                        fill=(255, 255, 0),
                        value=lambda: "Hello",
                        font=font.font_variant(size=128)
                    ),
                )
            )
        )
    ])


@approve_image
def test_frame_clipping():
    return time_rendering(name="viewport", widgets=[
        Translate(
            Coordinate(10, 10),
            Frame(
                dimensions=Dimension(300, 200),
                opacity=0.5,
                outline=(255, 255, 255),
                fill=(0, 0, 0),
                corner_radius=30,
                child=Composite(
                    CachingText(at=Coordinate(250, -20), value=lambda: "Hello", font=font.font_variant(size=48)),
                    CachingText(at=Coordinate(-30, 50), value=lambda: "World", font=font.font_variant(size=48))
                )
            )
        )
    ])


def time_rendering(name, widgets, dimensions: Dimension = Dimension(x=600, y=300), repeat=100):
    timer = PoorTimer(name)

    scene = Scene(dimensions, widgets)
    draw = None
    for i in range(0, repeat):
        draw = timer.time(lambda: scene.draw())

    if not is_make():
        draw.show()

    print(timer)
    return draw
