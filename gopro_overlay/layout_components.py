from datetime import timedelta

from .point import Coordinate
from .timeseries import Window
from .widgets import Text, date, time, CachingText, Composite
from .widgets_chart import SimpleChart
from .widgets_info import BigMetric
from .widgets_map import MovingMap, JourneyMap


def date_and_time(at, entry, font_title, font_metric):
    return Composite(
        CachingText(at + Coordinate(0, 0), date(lambda: entry().dt), font_title, align="right"),
        Text(at + Coordinate(0, 24), time(lambda: entry().dt), font_metric, align="right"),
    )


def gps_info(at, entry, font):
    return Composite(
        CachingText(at + Coordinate(0, 0), lambda: "GPS INFO", font, align="right"),
        Text(at + Coordinate(-130, 24), lambda: f"Lat: {entry().point.lat:0.6f}", font, align="right"),
        Text(at + Coordinate(0, 24), lambda: f"Lon: {entry().point.lon:0.6f}", font, align="right"),
    )


def journey_map(at, entry, **kwargs):
    return JourneyMap(
        at=at,
        location=lambda: entry().point,
        **kwargs
    )


def moving_map(at, entry, **kwargs):
    return MovingMap(
        at=at,
        location=lambda: entry().point,
        azimuth=lambda: entry().azi,
        **kwargs
    )


def metric_value(entry, accessor, converter, formatter):
    def value():
        v = accessor(entry())
        if v is not None:
            v = converter(v)
            return formatter(v.magnitude)
        return "-"

    return value


def text(cache=True, **kwargs):
    if cache:
        return CachingText(**kwargs)
    else:
        return Text(**kwargs)


def metric(entry, accessor, formatter, converter=lambda x: x, cache=True, **kwargs):
    return text(cache, value=metric_value(entry, accessor, converter, formatter), **kwargs)


def big_mph(at, entry, font_title, font_metric=None):
    if font_metric is None:
        font_metric = font_title.font_variant(size=160)

    return Composite(
        BigMetric(
            at,
            lambda: "MPH",
            lambda: f"{entry().speed.to('MPH').magnitude:.0f}" if entry().speed else "-",
            font_title=font_title,
            font_metric=font_metric
        )
    )


def gradient_chart(at, timeseries, entry, font_title):
    window = Window(timeseries, duration=timedelta(minutes=5), samples=256,
                    key=lambda e: e.alt, fmt=lambda v: v.to("meter").magnitude)
    return SimpleChart(
        at=at,
        value=lambda: window.view(entry().dt),
        font=font_title,
        filled=True
    )
