from typing import Callable

from .dimensions import Dimension
from .layout_components import metric_value
from .layout_xml import iattrib, rgbattr, fattrib, metric_accessor_from, attrib
from .layout_xml_attribute import allow_attributes
from .widgets.cairo.cairo import CairoAdapter
from .widgets.cairo.circuit import CairoCircuit
from .widgets.cairo.circuit import Line
from .widgets.cairo.gauge import CairoGauge270
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

    return lambda : Reading(metric() * scale)

def create_cairo_gauge_270(element, entry, converters, **kwargs) -> Widget:
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
        size=Dimension(size,size),
        widget=CairoGauge270(
          reading=as_reading(metric, min_value, max_value)
        )
    )