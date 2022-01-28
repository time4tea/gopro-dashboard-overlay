from PIL import ImageFont

from .layout_components import date_and_time, gps_info, big_mph, moving_map, journey_map, altitude, gradient, \
    gradient_chart, temperature, cadence, heartbeat
from .point import Coordinate
from .privacy import NoPrivacyZone
from .units import units
from .widgets import Scene
from .widgets_info import ComparativeEnergy


def speed_awareness_layout(renderer, font: ImageFont):
    def create(entry):
        font_title = font.font_variant(size=16)
        font_metric = font.font_variant(size=32)

        return [
            date_and_time(Coordinate(260, 30), entry, font_title, font_metric),
            gps_info(Coordinate(1900, 36), entry, font_title),
            big_mph(Coordinate(16, 800), entry, font_title),
            moving_map(Coordinate(1900 - 384, 100), entry, size=384, zoom=16, renderer=renderer),
            ComparativeEnergy(Coordinate(450, 850),
                              font=font_title,
                              speed=lambda: entry().speed,
                              person=units.Quantity(84, units.kg),
                              bike=units.Quantity(12, units.kg),
                              car=units.Quantity(2000, units.kg),
                              van=units.Quantity(3500, units.kg)
                              )
        ]

    return create


def standard_layout(renderer, timeseries, font, privacy=NoPrivacyZone()):
    def create(entry):
        font_title = font.font_variant(size=16)
        font_metric = font.font_variant(size=32)

        return [
            date_and_time(Coordinate(260, 30), entry, font_title, font_metric),
            gps_info(Coordinate(1900, 36), entry, font_title),
            moving_map(Coordinate(1900 - 256, 100), entry, size=256, zoom=16, renderer=renderer),
            journey_map(Coordinate(1900 - 256, 100 + 256 + 20), entry, privacy, renderer, timeseries),
            big_mph(Coordinate(16, 800), entry, font_title),
            altitude(Coordinate(16, 980), entry, font_metric, font_title),
            gradient(Coordinate(220, 980), entry, font_metric, font_title),
            gradient_chart(Coordinate(400, 980), timeseries, entry, font_title),
            temperature(Coordinate(1900, 820), entry, font_metric, font_title),
            cadence(Coordinate(1900, 900), entry, font_metric, font_title),
            heartbeat(Coordinate(1900, 980), entry, font_metric, font_title),
        ]

    return create


class Overlay:

    def __init__(self, timeseries, create_widgets):
        self.scene = Scene(create_widgets(self.entry))
        self.timeseries = timeseries
        self._entry = None

    def entry(self):
        return self._entry

    def draw(self, dt):
        self._entry = self.timeseries.get(dt)
        return self.scene.draw()
