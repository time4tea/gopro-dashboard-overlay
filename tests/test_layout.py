import geotiler

from gopro_overlay import fake
from gopro_overlay.layout import Layout
from tests.testenvironment import is_ci


def test_render_sample():

    timeseries = fake.fake_timeseries()

    overlay = Layout(timeseries, geotiler.render_map)

    draw = overlay.draw(timeseries.min)
    if not is_ci():
        draw.show()
