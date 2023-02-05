from typing import Callable

from cairo import LineCap

from .dimensions import Dimension
from .layout_components import metric_value
from .layout_xml import iattrib, rgbattr, fattrib, metric_accessor_from, attrib
from .layout_xml_attribute import allow_attributes
from .widgets.cairo.angle import Angle
from .widgets.cairo.cairo import CairoAdapter
from .widgets.cairo.circuit import CairoCircuit
from .widgets.cairo.circuit import Line
from .widgets.cairo.colour import Colour
from .widgets.cairo.gauge import CairoGaugeMarker
from .widgets.cairo.reading import Reading
from .widgets.widgets import Widget


@allow_attributes({"size", "rotate", "fill", "outline", "line-width", "loc-fill", "loc-outline", "loc-size"})
def create_cairo_circuit_map(element, entry, timeseries, **kwargs) -> Widget:
    size = iattrib(element, "size", d=256)
    rotation = iattrib(element, "rotate", d=0)

    return CairoAdapter(
        size=Dimension(size, size),
        widget=CairoCircuit(
            framemeta=timeseries,
            location=lambda: entry().point,
            line=Line(
                fill=rgbattr(element, "fill", d=(255, 255, 255)),
                outline=rgbattr(element, "outline", d=(255, 0, 0)),
                width=fattrib(element, "line-width", d=0.01),
            ),
            loc=Line(
                fill=rgbattr(element, "loc-fill", d=(0, 0, 255)),
                outline=rgbattr(element, "loc-outline", d=(0, 0, 0)),
                width=fattrib(element, "loc-size", d=0.01 * 1.1)
            )
        ),
        rotation=rotation,
    )


def as_reading(metric, min_value, max_value) -> Callable[[], Reading]:
    range = max_value - min_value
    scale = 1.0 / range

    return lambda: Reading(metric() * scale)


def cap_from(name):
    caps = {
        "square": LineCap.SQUARE,
        "butt": LineCap.BUTT,
        "round": LineCap.ROUND
    }
    if name not in caps:
        raise IOError(f"Cap {name} is not recognised. Should be one of '{list(caps.keys())}'")
    return caps[name]


@allow_attributes({"size", "min", "max", "metric", "units", "start", "length",
                   "sectors", "tick-rgb", "gauge-rgb", "dot-outer-rgb", "dot-inner-rgb", "cap"})
def create_cairo_gauge_marker(element, entry, converters, **kwargs) -> Widget:
    size = iattrib(element, "size", d=256)

    min_value = iattrib(element, "min", d=0)
    max_value = iattrib(element, "max", d=50)

    metric = metric_value(
        entry,
        accessor=metric_accessor_from(attrib(element, "metric")),
        converter=converters.converter(attrib(element, "units", d=None)),
        formatter=lambda q: q.m,
        default=0
    )

    return CairoAdapter(
        size=Dimension(size, size),
        widget=CairoGaugeMarker(
            reading=as_reading(metric, min_value, max_value),
            start=Angle(degrees=iattrib(element, "start", d=90)),
            length=Angle(degrees=iattrib(element, "length", d=270)),
            sectors=iattrib(element, "sectors", d=6),
            tick_colour=Colour.from_pil(*rgbattr(element, "tick-rgb", d=(255, 255, 255))),
            gauge_colour=Colour.from_pil(*rgbattr(element, "gauge-rgb", d=(0, 191, 255))),
            marker_outer=Colour.from_pil(*rgbattr(element, "dot-outer-rgb", d=(255, 255, 255, 180))),
            marker_inner=Colour.from_pil(*rgbattr(element, "dot-inner-rgb", d=(0, 192, 255))),
            cap=cap_from(attrib(element, "cap", d="square")),
        )
    )
