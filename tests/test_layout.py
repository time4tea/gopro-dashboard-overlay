import random
from datetime import timedelta

from gopro_overlay import fake
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.layout import Layout, SpeedAwarenessLayout
from gopro_overlay.timing import PoorTimer
from tests.approval import approve_image
from tests.testenvironment import is_ci

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

timeseries = fake.fake_timeseries(length=timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)

renderer = CachingRenderer()


@approve_image
def test_render_default_layout():
    with renderer.open() as map_renderer:
        return time_layout("default", Layout(timeseries, map_renderer))


@approve_image
def test_render_speed_layout():
    with renderer.open() as map_renderer:
        return time_layout("speed", SpeedAwarenessLayout(timeseries, map_renderer))


def time_layout(name, layout, repeat=20):
    timer = PoorTimer(name)

    for i in range(0, repeat):
        draw = timer.time(lambda: layout.draw(timeseries.min))

    print(timer)

    if not is_ci():
        draw.show()

    return draw
