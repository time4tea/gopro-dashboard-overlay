from datetime import timedelta

from gopro_overlay import fake
from gopro_overlay.geo import CachingRenderer
from gopro_overlay.layout import Layout
from gopro_overlay.timing import PoorTimer
from tests.testenvironment import is_ci


def test_render_sample():
    timeseries = fake.fake_timeseries(length=timedelta(minutes=10), step=timedelta(seconds=1))

    renderer = CachingRenderer()

    with renderer.open() as map_renderer:

        overlay = Layout(timeseries, map_renderer)

        timer = PoorTimer("layout")

        for i in range(0, 20):
            draw = timer.time(lambda: overlay.draw(timeseries.min))

    print(timer)

    if not is_ci():
        draw.show()
