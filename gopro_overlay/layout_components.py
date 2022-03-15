from datetime import timedelta

from .timeseries import Window
from .widgets import Text, CachingText
from .widgets_chart import SimpleChart
from .widgets_map import MovingMap, JourneyMap


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


def metric_value(entry, accessor, converter, formatter, default="-"):
    def value():
        v = accessor(entry())
        if v is not None:
            v = converter(v)
            return formatter(v.magnitude)
        return default

    return value


def text(cache=True, **kwargs):
    if cache:
        return CachingText(**kwargs)
    else:
        return Text(**kwargs)


def metric(entry, accessor, formatter, converter=lambda x: x, cache=True, **kwargs):
    return text(cache, value=metric_value(entry, accessor, converter, formatter), **kwargs)


def gradient_chart(at, timeseries, entry, font_title):
    window = Window(timeseries, duration=timedelta(minutes=5), samples=256,
                    key=lambda e: e.alt, fmt=lambda v: v.to("meter").magnitude)
    return SimpleChart(
        at=at,
        value=lambda: window.view(entry().dt),
        font=font_title,
        filled=True
    )
