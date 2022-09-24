from .widgets.text import CachingText, Text
from .widgets.map import MovingMap, JourneyMap


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
