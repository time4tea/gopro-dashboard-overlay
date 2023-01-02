import random
from datetime import timedelta

import pytest
from PIL import ImageFont

from gopro_overlay import fake, arguments
from gopro_overlay.dimensions import Dimension
from gopro_overlay.framemeta import gps_framemeta
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.layout import Overlay
from gopro_overlay.layout_components import moving_map, journey_map
from gopro_overlay.point import Coordinate
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.timeunits import timeunits
from gopro_overlay.timing import PoorTimer
from gopro_overlay.units import units
from gopro_overlay.widgets.map import MovingJourneyMap, view_window
from gopro_overlay.widgets.widgets import Translate, Frame
from tests.approval import approve_image
from tests.test_widgets import time_rendering
from tests.testenvironment import is_make

font = ImageFont.truetype(font='Roboto-Medium.ttf', size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)

renderer = CachingRenderer(cache_dir=arguments.default_config_location)


def a_real_journey(name, dimension, f_scene):
    with open("meta/gopro-meta.gpmd", "rb") as f:
        data = f.read()

    framemeta = gps_framemeta(meta=GoproMeta.parse(data), units=units)

    overlay = Overlay(
        dimensions=dimension,
        framemeta=framemeta,
        create_widgets=f_scene
    )

    stepper = framemeta.stepper(timeunits(seconds=0.1))

    timer = PoorTimer(name)

    image = None

    for index, dt in enumerate(stepper.steps()):
        image = timer.time(lambda: overlay.draw(dt))

    if not is_make():
        image.show()
    print(timer)


@pytest.mark.skip(reason="slow")
def test_rendering_moving_map_journey():
    with renderer.open() as r:
        a_real_journey(
            name="rendering_moving_map_journey",
            dimension=Dimension(256, 256),
            f_scene=lambda entry: [moving_map(
                at=Coordinate(0, 0),
                entry=entry,
                size=256,
                zoom=13,
                renderer=r
            )]
        )


@approve_image
def test_render_journey_map():
    with renderer.open() as map_renderer:
        return time_rendering("journey_map", widgets=[
            journey_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, renderer=map_renderer,
                        timeseries=ts, privacy_zone=NoPrivacyZone())
        ])


@approve_image
def test_render_journey_map_rounded():
    with renderer.open() as map_renderer:
        return time_rendering("journey_map", widgets=[
            journey_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, renderer=map_renderer,
                        timeseries=ts, privacy_zone=NoPrivacyZone(), corner_radius=35)
        ])


@approve_image
def test_render_journey_very_transparent():
    with renderer.open() as map_renderer:
        return time_rendering("journey_map", widgets=[
            journey_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, renderer=map_renderer,
                        timeseries=ts, privacy_zone=NoPrivacyZone(), opacity=0.1)
        ])


@approve_image
def test_render_moving_map():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer)
        ])


@approve_image
def test_render_moving_map_not_transparent():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map_not_transparent", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer,
                       opacity=1.0)
        ])


@approve_image
def test_render_moving_map_very_transparent():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map_very_transparent", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer,
                       opacity=0.2)
        ])


@approve_image
def test_render_moving_map_rounded():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map_rounded", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer,
                       corner_radius=35)
        ])


@approve_image
def test_render_moving_map_very_rounded():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map_very_rounded", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer,
                       corner_radius=128)
        ])


@approve_image
def test_moving_journey_map_at_start():
    with renderer.open() as map_renderer:
        return time_rendering(
            "test_moving_journey_map_at_start",
            widgets=[
                MovingJourneyMap(
                    timeseries=ts,
                    privacy_zone=NoPrivacyZone(),
                    location=lambda: ts.get(ts.min).point,
                    size=256,
                    zoom=15,
                    renderer=map_renderer,
                ),
            ])


@approve_image
def test_moving_journey_map_halfway():
    ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng, point_step=0.0005)

    with renderer.open() as map_renderer:
        return time_rendering(
            "test_moving_journey_map_halfway",
            widgets=[
                Translate(
                    Coordinate(256, 0),
                    MovingJourneyMap(
                        timeseries=ts,
                        privacy_zone=NoPrivacyZone(),
                        location=lambda: ts.get(ts.min + ((ts.max - ts.min) / 3)).point,
                        size=256,
                        zoom=17,
                        renderer=map_renderer,
                    )
                ),
            ])


@approve_image
def test_moving_journey_map_in_frame():
    ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng, point_step=0.0005)

    with renderer.open() as map_renderer:
        return time_rendering(
            "test_moving_journey_map_halfway",
            widgets=[
                Translate(
                    Coordinate(256, 0),
                    Frame(
                        dimensions=Dimension(256, 256),
                        opacity=0.7,
                        corner_radius=128,
                        child=MovingJourneyMap(
                            timeseries=ts,
                            privacy_zone=NoPrivacyZone(),
                            location=lambda: ts.get(ts.min + ((ts.max - ts.min) / 3)).point,
                            size=256,
                            zoom=17,
                            renderer=map_renderer,
                        )
                    )
                ),
            ])


def test_view_window():
    window = view_window(size=256, d=1336)

    assert window(1336) == (1336 - 256, 1336)
    assert window(0) == (0, 256)
    assert window(1) == (0, 256)
    assert window(128) == (0, 256)
    assert window(129) == (1, 257)
    assert window(1336 - 100) == (1336 - 256, 1336)
