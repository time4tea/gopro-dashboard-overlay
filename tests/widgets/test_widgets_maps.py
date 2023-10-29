from datetime import timedelta

import pytest

from gopro_overlay import fake, arguments
from gopro_overlay.dimensions import Dimension
from gopro_overlay.framemeta import gps_framemeta
from gopro_overlay.geo import MapRenderer, MapStyler
from gopro_overlay.gpmd import GPMD, GPSFix
from gopro_overlay.layout import Overlay
from gopro_overlay.layout_components import moving_map, journey_map
from gopro_overlay.point import Coordinate
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.timeunits import timeunits
from gopro_overlay.timing import PoorTimer
from gopro_overlay.units import units
from gopro_overlay.widgets.map import MovingJourneyMap, view_window
from gopro_overlay.widgets.widgets import Translate, Frame, SimpleFrameSupplier
from tests.widgets import test_widgets_setup
from tests.approval import approve_image
from tests.widgets.test_widgets import time_rendering
from tests.widgets.test_widgets_setup import rng
from tests.testenvironment import is_make

font = test_widgets_setup.font
ts = test_widgets_setup.ts

arguments.default_config_location.mkdir(parents=True, exist_ok=True)
renderer = MapRenderer(cache_dir=arguments.default_config_location, styler=MapStyler())


def a_real_journey(name, dimension, f_scene):
    with open("../meta/gopro-meta.gpmd", "rb") as f:
        data = f.read()

    framemeta = gps_framemeta(meta=GPMD.parse(data), units=units)

    supplier = SimpleFrameSupplier(dimension)

    overlay = Overlay(
        framemeta=framemeta,
        create_widgets=f_scene
    )

    stepper = framemeta.stepper(timeunits(seconds=0.1))

    timer = PoorTimer(name)

    image = None

    for index, dt in enumerate(stepper.steps()):
        image = timer.time(lambda: overlay.draw(dt, supplier.drawing_frame()))

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


@pytest.mark.gfx
@approve_image
def test_render_journey_map():
    with renderer.open() as map_renderer:
        return time_rendering("journey_map", widgets=[
            journey_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, renderer=map_renderer,
                        timeseries=ts, privacy_zone=NoPrivacyZone())
        ])


@pytest.mark.gfx
@approve_image
def test_render_journey_map_rounded():
    with renderer.open() as map_renderer:
        return time_rendering("journey_map", widgets=[
            journey_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, renderer=map_renderer,
                        timeseries=ts, privacy_zone=NoPrivacyZone(), corner_radius=35)
        ])


@pytest.mark.gfx
@approve_image
def test_render_journey_map_rounded_when_no_data_was_locked_issue_103():

    ts.process(lambda e: {"gpsfix": GPSFix.NO.value})

    with renderer.open() as map_renderer:
        return time_rendering("journey_map", widgets=[
            journey_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, renderer=map_renderer,
                        timeseries=ts, privacy_zone=NoPrivacyZone(), corner_radius=35)
        ])


@pytest.mark.gfx
@approve_image
def test_render_journey_very_transparent():

    with renderer.open() as map_renderer:
        return time_rendering("journey_map", widgets=[
            journey_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, renderer=map_renderer,
                        timeseries=ts, privacy_zone=NoPrivacyZone(), opacity=0.1)
        ])


@pytest.mark.gfx
@approve_image
def test_render_moving_map():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer)
        ])


@pytest.mark.gfx
@approve_image
def test_render_moving_map_not_transparent():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map_not_transparent", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer,
                       opacity=1.0)
        ])


@pytest.mark.gfx
@approve_image
def test_render_moving_map_very_transparent():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map_very_transparent", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer,
                       opacity=0.2)
        ])


@pytest.mark.gfx
@approve_image
def test_render_moving_map_rounded():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map_rounded", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer,
                       corner_radius=35)
        ])


@pytest.mark.gfx
@approve_image
def test_render_moving_map_very_rounded():
    with renderer.open() as map_renderer:
        return time_rendering("moving_map_very_rounded", widgets=[
            moving_map(at=Coordinate(100, 20), entry=lambda: ts.get(ts.min), size=256, zoom=15, renderer=map_renderer,
                       corner_radius=128)
        ])




@pytest.mark.gfx
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


@pytest.mark.gfx
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


@pytest.mark.gfx
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
