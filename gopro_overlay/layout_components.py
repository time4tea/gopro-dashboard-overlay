from datetime import timedelta

from .point import Coordinate
from .timeseries import Window
from .widgets import Text, date, time, CachingText, Composite
from .widgets_chart import SimpleChart
from .widgets_info import BigMetric, IconPanel
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


def journey_map(at, entry, privacy_zone, renderer, timeseries, size=256):
    return JourneyMap(
        at=at,
        timeseries=timeseries,
        location=lambda: entry().point,
        size=size,
        renderer=renderer,
        privacy_zone=privacy_zone
    )


def moving_map(at, entry, size, zoom, renderer):
    return MovingMap(
        at=at,
        location=lambda: entry().point,
        azimuth=lambda: entry().azi,
        renderer=renderer,
        size=size,
        zoom=zoom
    )


def metric_value(entry, accessor, converter, formatter):
    def value():
        v = accessor(entry())
        if v is not None:
            v = converter(v)
            return formatter(v.magnitude)
        return "-"

    return value


def metric(at, entry, accessor, formatter, font, converter=lambda x: x, align="left", cache=True):
    if cache:
        return CachingText(
            at,
            metric_value(entry, accessor, converter, formatter),
            font,
            align
        )
    else:
        return Text(
            at,
            metric_value(entry, accessor, converter, formatter),
            font,
            align
        )


def text_dynamic(at, string, font, align="left", cache=True):
    if cache:
        return CachingText(at, string, font, align)
    else:
        return Text(at, string, font, align)


def text(at, string, font, align="left", cache=True):
    if cache:
        return CachingText(at, lambda: string, font, align)
    else:
        return Text(at, lambda: string, font, align)


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


def heartbeat(at, entry, font_metric, font_title):
    return IconPanel(
        at=at,
        icon="heartbeat.png",
        title=lambda: "BPM",
        value=lambda: f"{entry().hr.magnitude:.0f}" if entry().hr else "-",
        align="right",
        title_font=font_title,
        value_font=font_metric
    )


def cadence(at, entry, font_metric, font_title):
    return IconPanel(
        at=at,
        icon="gauge.png",
        title=lambda: "RPM",
        value=lambda: f"{entry().cad.magnitude:.0f}" if entry().cad else "-",
        align="right",
        title_font=font_title,
        value_font=font_metric
    )


def temperature(at, entry, font_metric, font_title):
    return IconPanel(
        at=at,
        icon="thermometer.png",
        title=lambda: "TEMP(C)",
        value=lambda: f"{entry().atemp.magnitude:.0f}" if entry().atemp is not None else "-",
        align="right",
        title_font=font_title,
        value_font=font_metric
    )


def gradient(at, entry, font_metric, font_title):
    return IconPanel(
        at=at,
        icon="slope-triangle.png",
        title=lambda: "SLOPE(%)",
        value=lambda: f"{entry().grad.magnitude:.1f}" if entry().grad else "-",
        align="left",
        title_font=font_title,
        value_font=font_metric
    )


def altitude(at, entry, font_metric, font_title):
    return IconPanel(
        at=at,
        icon="mountain.png",
        title=lambda: "ALT(m)",
        value=lambda: f"{entry().alt.to('m').magnitude:.1f}" if entry().alt else "-",
        align="left",
        title_font=font_title,
        value_font=font_metric
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
