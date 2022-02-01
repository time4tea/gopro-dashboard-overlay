import importlib
import random
from datetime import timedelta

from gopro_overlay import fake
from gopro_overlay import layouts
from gopro_overlay.font import load_font
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.layout import Overlay, standard_layout, speed_awareness_layout
from gopro_overlay.layout_xml import layout_from_xml
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.timing import PoorTimer
from tests.approval import approve_image
from tests.testenvironment import is_make

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

timeseries = fake.fake_timeseries(length=timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)

renderer = CachingRenderer()

font = load_font("Roboto-Medium.ttf")


@approve_image
def test_render_default_layout():
    # Avg: 0.02276, Rate: 43.93
    with renderer.open() as map_renderer:
        return time_layout("default", Overlay(timeseries, standard_layout(map_renderer, timeseries, font)))


@approve_image
def test_render_speed_layout():
    with renderer.open() as map_renderer:
        return time_layout("speed", Overlay(timeseries, speed_awareness_layout(map_renderer, font=font)))


@approve_image
def test_render_xml_layout():
    with importlib.resources.path(layouts, "example.xml") as fn:
        with open(fn) as f:
            xmldoc = f.read()

    with renderer.open() as map_renderer:
        return time_layout("xml", Overlay(timeseries, layout_from_xml(xmldoc, map_renderer, timeseries, font,
                                                                      privacy=NoPrivacyZone())))


@approve_image
def test_render_xml_component():
    xmldoc = """<layout>
        <composite name="bob" x="200" y="200">
            <component type="text" x="0" y="0" size="32" cache="False">Text</component> 
            <component type="text" x="50" y="50" size="64">Text</component> 
            <component type="text" x="150" y="150" size="128" >Text</component> 
        </composite>
    </layout>
    """

    with renderer.open() as map_renderer:
        return time_layout("xml", Overlay(timeseries, layout_from_xml(xmldoc, map_renderer, timeseries, font,
                                                                      privacy=NoPrivacyZone())))


@approve_image
def test_render_xml_component_with_exclusions():
    xmldoc = """<layout>
        <composite name="bob" x="200" y="200">
            <component type="text" x="0" y="0" size="32" cache="False">Bob</component> 
            <component type="text" x="50" y="50" size="64">Bob</component> 
            <component type="text" x="150" y="150" size="128" >Bob</component> 
        </composite>
        <composite name="alice" x="400" y="200">
            <component type="text" x="0" y="0" size="32" cache="False">Alice</component> 
            <component type="text" x="50" y="50" size="64">Alice</component> 
            <component type="text" x="150" y="150" size="128" >Alice</component> 
        </composite>
    </layout>
    """

    with renderer.open() as map_renderer:
        return time_layout("xml",
                           Overlay(
                               timeseries,
                               layout_from_xml(
                                   xmldoc,
                                   map_renderer,
                                   timeseries,
                                   font,
                                   privacy=NoPrivacyZone(),
                                   include=lambda name: name == "alice"
                               )
                           ))


def time_layout(name, layout, repeat=20):
    timer = PoorTimer(name)

    for i in range(0, repeat):
        draw = timer.time(lambda: layout.draw(timeseries.min))

    print(timer)

    if not is_make():
        draw.show()

    return draw
