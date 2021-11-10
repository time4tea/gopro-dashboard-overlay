import itertools
from datetime import timedelta
from sys import stderr

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


def load_font(font: str, size: int):
    try:
        return ImageFont.truetype(font=font, size=size)
    except OSError as e:
        print(f"Can't find the font {font}", file=stderr)
        raise e


class SpeedAwarenessLayout:
    def __init__(self, timeseries, map_renderer, font_name: str):
        self.map_renderer = map_renderer
        self.timeseries = timeseries
        self._entry = None

        font_title = load_font(font=font_name, size=16)
        font_metric = load_font(font=font_name, size=32)

        self.scene = Scene(
            list(itertools.chain(
                date_and_time(Coordinate(260, 30), self.entry, font_title, font_metric),
                gps_info(Coordinate(1900, 36), self.entry, font_title),
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

    def __init__(self, timeseries, map_renderer, privacy_zone=NoPrivacyZone(), font_name: str = None):
        self.map_renderer = map_renderer
        self.timeseries = timeseries
        self._entry = None

        try:
            font_title = load_font(font=font_name, size=16)
            font_metric = load_font(font=font_name, size=32)
        except OSError as e:
            print(f"Can't find {font_name}", file=stderr)
            raise e

        window = Window(timeseries, duration=timedelta(minutes=5), samples=256,
                        key=lambda e: e.alt, fmt=lambda v: v.to("meter").magnitude)

        self.scene = Scene(
            list(itertools.chain(
                date_and_time(Coordinate(260, 30), self.entry, font_title, font_metric),
                gps_info(Coordinate(1900, 36), self.entry, font_title),
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
