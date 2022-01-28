import itertools
from datetime import timedelta

from PIL import ImageFont

from .point import Coordinate
from .privacy import NoPrivacyZone
from .timeseries import Window
from .units import units
from .widgets import Text, date, time, Scene, CachingText
from .widgets_chart import SimpleChart
from .widgets_info import LeftInfoPanel, RightInfoPanel, BigMetric, ComparativeEnergy
from .widgets_map import MovingMap, JourneyMap


def date_and_time(at, entry, font_title, font_metric):
    return [
        CachingText(at + Coordinate(0, 0), date(lambda: entry().dt), font_title, align="right"),
        Text(at + Coordinate(0, 24), time(lambda: entry().dt), font_metric, align="right"),
    ]


def gps_info(at, entry, font_title):
    return [
        CachingText(at + Coordinate(0, 0), lambda: "GPS INFO", font_title, align="right"),
        Text(at + Coordinate(-130, 24), lambda: f"Lat: {entry().point.lat:0.6f}", font_title, align="right"),
        Text(at + Coordinate(0, 24), lambda: f"Lon: {entry().point.lon:0.6f}", font_title, align="right"),
    ]


def maps(entry, renderer, timeseries, privacy_zone):
    return [
        MovingMap(
            at=Coordinate(1900 - 256, 100),
            location=lambda: entry().point,
            azimuth=lambda: entry().azi,
            renderer=renderer,
            zoom=16
        ),
        JourneyMap(
            at=Coordinate(1900 - 256, 100 + 256 + 20),
            timeseries=timeseries,
            location=lambda: entry().point,
            renderer=renderer,
            privacy_zone=privacy_zone
        ),
    ]


def big_mph(entry, font_title):
    return [
        BigMetric(
            Coordinate(16, 800),
            lambda: "MPH",
            lambda: f"{entry().speed.to('MPH').magnitude:.0f}" if entry().speed else "-",
            font_title
        )
    ]


def speed_awareness_layout(renderer, font: ImageFont):
    def create(entry):
        font_title = font.font_variant(size=16)
        font_metric = font.font_variant(size=32)

        return list(itertools.chain(
            date_and_time(Coordinate(260, 30), entry, font_title, font_metric),
            gps_info(Coordinate(1900, 36), entry, font_title),
            big_mph(entry, font_title),
            [
                MovingMap(
                    size=384,
                    at=Coordinate(1900 - 384, 100),
                    location=lambda: entry().point,
                    azimuth=lambda: entry().azi,
                    renderer=renderer,
                    zoom=16
                ),
                ComparativeEnergy(Coordinate(450, 850),
                                  font=font_title,
                                  speed=lambda: entry().speed,
                                  person=units.Quantity(84, units.kg),
                                  bike=units.Quantity(12, units.kg),
                                  car=units.Quantity(2000, units.kg),
                                  van=units.Quantity(3500, units.kg)
                                  )

            ]
        )
        )

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


def standard_layout(renderer, timeseries, font, privacy=NoPrivacyZone()):
    def create(entry):
        font_title = font.font_variant(size=16)
        font_metric = font.font_variant(size=32)

        window = Window(timeseries, duration=timedelta(minutes=5), samples=256,
                        key=lambda e: e.alt, fmt=lambda v: v.to("meter").magnitude)

        return list(itertools.chain(
            date_and_time(Coordinate(260, 30), entry, font_title, font_metric),
            gps_info(Coordinate(1900, 36), entry, font_title),
            maps(entry, renderer, timeseries, privacy),
            big_mph(entry, font_title),
            [
                LeftInfoPanel(
                    Coordinate(16, 980),
                    "mountain.png",
                    lambda: "ALT(m)",
                    lambda: f"{entry().alt.to('m').magnitude:.1f}" if entry().alt else "-",
                    font_title,
                    font_metric
                ),
                LeftInfoPanel(
                    Coordinate(220, 980),
                    "slope-triangle.png",
                    lambda: "SLOPE(%)",
                    lambda: f"{entry().grad.magnitude:.1f}" if entry().grad else "-",
                    font_title,
                    font_metric
                ),
                SimpleChart(
                    at=Coordinate(400, 980),
                    value=lambda: window.view(entry().dt),
                    font=font_title,
                    filled=True
                ),
                RightInfoPanel(
                    Coordinate(1900, 820),
                    "thermometer.png",
                    lambda: "TEMP(C)",
                    lambda: f"{entry().atemp.magnitude:.0f}" if entry().atemp is not None else "-",
                    font_title,
                    font_metric
                ),
                RightInfoPanel(
                    Coordinate(1900, 900),
                    "gauge.png",
                    lambda: "RPM",
                    lambda: f"{entry().cad.magnitude:.0f}" if entry().cad else "-",
                    font_title,
                    font_metric
                ),
                RightInfoPanel(
                    Coordinate(1900, 980),
                    "heartbeat.png",
                    lambda: "BPM",
                    lambda: f"{entry().hr.magnitude:.0f}" if entry().hr else "-",
                    font_title,
                    font_metric
                ),
            ])
        )

    return create
