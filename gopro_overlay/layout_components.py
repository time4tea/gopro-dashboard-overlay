from typing import Callable, TypeVar, Optional

from pint import Quantity

from .entry import Entry
from .widgets.map import MovingMap, JourneyMap
from .widgets.text import CachingText, Text
from .widgets.widgets import Widget


def journey_map(at, entry, **kwargs) -> Widget:
    return JourneyMap(
        at=at,
        location=lambda: entry().point,
        waypoints=lambda: entry().custom["waypoints"],
        **kwargs
    )


def moving_map(at, entry, **kwargs) -> Widget:
    return MovingMap(
        at=at,
        location=lambda: entry().point,
        azimuth=lambda: entry().azi,
        **kwargs
    )


T = TypeVar("T")


def metric_value(
        entry: Callable[[], Optional[Entry]],
        accessor: Callable[[Entry], Optional[Quantity]],
        converter: Callable[[Quantity], Optional[Quantity]],
        formatter: Callable[[Quantity], T],
        default: T = "-"
) -> Callable[[], T]:
    def value() -> T:
        e = accessor(entry())
        if e is not None:
            v = converter(e)
            if v is not None:
                return formatter(v)
        return default

    return value


def text(cache=True, **kwargs) -> Widget:
    if cache:
        return CachingText(**kwargs)
    else:
        return Text(**kwargs)


def metric(entry, accessor, formatter, converter=lambda x: x, cache=True, **kwargs):
    return text(cache, value=metric_value(entry, accessor, converter, formatter), **kwargs)
