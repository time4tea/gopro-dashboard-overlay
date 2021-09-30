import itertools
from datetime import timedelta

from PIL import ImageFont

from .point import Coordinate
from .privacy import NoPrivacyZone
from .timeseries import Window
from .units import units
from .widgets import Text, date, time, Scene
from .widgets_chart import SimpleChart
from .widgets_info import LeftInfoPanel, RightInfoPanel, BigMetric, ComparativeEnergy
from .widgets_map import MovingMap, JourneyMap


def date_and_time(entry, font_title, font_metric):
    return [
        Text(Coordinate(260, 36), date(lambda: entry().dt), font_title, align="right"),
        Text(Coordinate(260, 60), time(lambda: entry().dt), font_metric, align="right"),
    ]


def gps_info(entry, font_title):
    return [
        Text(Coordinate(1900, 36), lambda: "GPS INFO", font_title, align="right"),
        Text(Coordinate(1780, 60), lambda: f"Lat: {entry().point.lat:0.6f}", font_title, align="right"),
        Text(Coordinate(1900, 60), lambda: f"Lon: {entry().point.lon:0.6f}", font_title, align="right"),
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


class SpeedAwarenessLayout:
    def __init__(self, timeseries, map_renderer):
        self.map_renderer = map_renderer
        self.timeseries = timeseries
        self._entry = None

        font_title = ImageFont.truetype(font="Roboto-Medium.ttf", size=16)
        font_metric = ImageFont.truetype(font="Roboto-Medium.ttf", size=32)

        self.scene = Scene(
            list(itertools.chain(
                date_and_time(self.entry, font_title, font_metric),
                gps_info(self.entry, font_title),
                big_mph(self.entry, font_title),
                [
                    MovingMap(
                        size=384,
                        at=Coordinate(1900 - 384, 100),
                        location=lambda: self._entry.point,
                        azimuth=lambda: self._entry.azi,
                        renderer=map_renderer,
                        zoom=16
                    ),
                    ComparativeEnergy(Coordinate(450, 850),
                                      font=font_title,
                                      speed=lambda: self._entry.speed,
                                      person=units.Quantity(60, units.kg),
                                      bike=units.Quantity(12, units.kg),
                                      car=units.Quantity(2678, units.kg),
                                      van=units.Quantity(3500, units.kg)
                                      )

                ]
            ))
        )

    def entry(self):
        return self._entry

    def draw(self, dt):
        self._entry = self.timeseries.get(dt)
        return self.scene.draw()


class Layout:

    def __init__(self, timeseries, map_renderer, privacy_zone=NoPrivacyZone()):
        self.map_renderer = map_renderer
        self.timeseries = timeseries
        self._entry = None

        font_title = ImageFont.truetype(font="Roboto-Medium.ttf", size=16)
        font_metric = ImageFont.truetype(font="Roboto-Medium.ttf", size=32)

        window = Window(timeseries, duration=timedelta(minutes=5), samples=256,
                        key=lambda e: e.alt.to("meter").magnitude)

        self.scene = Scene(
            list(itertools.chain(
                date_and_time(self.entry, font_title, font_metric),
                gps_info(self.entry, font_title),
                maps(self.entry, map_renderer, timeseries, privacy_zone),
                big_mph(self.entry, font_title),
                [
                    LeftInfoPanel(
                        Coordinate(16, 980),
                        "mountain.png",
                        lambda: "ALT(m)",
                        lambda: f"{self._entry.alt.to('m').magnitude:.1f}" if self._entry.alt else "-",
                        font_title,
                        font_metric
                    ),
                    LeftInfoPanel(
                        Coordinate(220, 980),
                        "slope-triangle.png",
                        lambda: "SLOPE(%)",
                        lambda: f"{self._entry.grad.magnitude:.1f}" if self._entry.grad else "-",
                        font_title,
                        font_metric
                    ),
                    SimpleChart(
                        at=Coordinate(400, 980),
                        value=lambda: window.view(self._entry.dt),
                        font=font_title,
                        filled=True
                    ),
                    RightInfoPanel(
                        Coordinate(1900, 820),
                        "thermometer.png",
                        lambda: "TEMP(C)",
                        lambda: f"{self._entry.atemp.magnitude:.0f}" if self._entry.atemp is not None else "-",
                        font_title,
                        font_metric
                    ),
                    RightInfoPanel(
                        Coordinate(1900, 900),
                        "gauge.png",
                        lambda: "RPM",
                        lambda: f"{self._entry.cad.magnitude:.0f}" if self._entry.cad else "-",
                        font_title,
                        font_metric
                    ),
                    RightInfoPanel(
                        Coordinate(1900, 980),
                        "heartbeat.png",
                        lambda: "BPM",
                        lambda: f"{self._entry.hr.magnitude:.0f}" if self._entry.hr else "-",
                        font_title,
                        font_metric
                    ),
                ])
            )
        )

    def entry(self):
        return self._entry

    def draw(self, dt):
        self._entry = self.timeseries.get(dt)
        return self.scene.draw()
