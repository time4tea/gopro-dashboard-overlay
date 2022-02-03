import random
from datetime import timedelta

from PIL import ImageFont

from gopro_overlay import fake
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.layout_components import moving_map, journey_map
from gopro_overlay.point import Coordinate
from gopro_overlay.privacy import NoPrivacyZone
from tests.approval import approve_image
from tests.test_widgets import time_rendering

font = ImageFont.truetype(font='Roboto-Medium.ttf', size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_timeseries(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)

renderer = CachingRenderer()


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
