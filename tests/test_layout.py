import random
from datetime import timedelta

from gopro_overlay import fake
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


xmldoc = """<layout>
  <component type="date_and_time" x="260" y="30"  size_time="48" />
  <component type="gps_info"      x="1900" y="36" size="16" />
  <component type="moving_map"    x="1644" y="100" />
  <component type="journey_map"   x="1644" y="376" />
  <component type="big_mph"       x="16"   y="800" />
  <component type="gradient"      x="220"  y="980" />
  <component type="gradient_chart" x="400"  y="980" />
  <component type="temperature"   x="1900" y="820" />
  <component type="cadence"       x="1900" y="900" />
  <component type="heartbeat"     x="1900" y="980" />
</layout>
"""


@approve_image
def test_render_xml_layout():
    with renderer.open() as map_renderer:
        return time_layout("xml", Overlay(timeseries, layout_from_xml(xmldoc, map_renderer, timeseries, font,
                                                                      privacy=NoPrivacyZone())))


def time_layout(name, layout, repeat=20):
    timer = PoorTimer(name)

    for i in range(0, repeat):
        draw = timer.time(lambda: layout.draw(timeseries.min))

    print(timer)

    if not is_make():
        draw.show()

    return draw
