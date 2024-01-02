from typing import Callable, Optional

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
from .widgets.cairo.gauge_donut import CairoGaugeDonutAnnotated
from .widgets.cairo.gauge_marker import CairoGaugeMarker
from .widgets.cairo.gauge_round_254 import CairoGaugeRoundAnnotated
from .widgets.cairo.gauge_sector_254 import CairoGaugeSectorAnnotated
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


def cairo_colour(t) -> Optional[Colour]:
    if t is None:
        return None
    return Colour.from_pil(*t)


@allow_attributes({"size", "min", "max", "metric", "units", "start", "length",
                   "sectors", "tick-rgb", "background-rgb", "gauge-rgb", "dot-outer-rgb", "dot-inner-rgb", "cap"})
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
            start=Angle(degrees=iattrib(element, "start", d=0)),
            length=Angle(degrees=iattrib(element, "length", d=270)),
            sectors=iattrib(element, "sectors", d=6),
            tick_colour=colour_attr(element, "tick-rgb", (255, 255, 255)),
            background_colour=colour_attr(element, "background-rgb", None),
            gauge_colour=colour_attr(element, "gauge-rgb", (0, 191, 255)),
            marker_outer=colour_attr(element, "dot-outer-rgb", None),
            marker_inner=colour_attr(element, "dot-inner-rgb", None),
            cap=cap_from(attrib(element, "cap", d="square")),
        )
    )


def colour_attr(element, attr, d):
    return cairo_colour(rgbattr(element, attr, d=d))


@allow_attributes({"size", "min", "max", "metric", "units", "start", "length",
                   "sectors",
                   "background-rgb",
                   "major-ann-rgb", "minor-ann-rgb",
                   "major-tick-rgb", "minor-tick-rgb",
                   "needle-rgb",
                   })
def create_cairo_gauge_round_annotated(element, entry, converters, **kwargs) -> Widget:
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
        widget=CairoGaugeRoundAnnotated(
            reading=as_reading(metric, min_value, max_value),
            start=Angle(degrees=iattrib(element, "start", d=143)),
            length=Angle(degrees=iattrib(element, "length", d=254)),
            sectors=iattrib(element, "sectors", d=5),
            background_colour=colour_attr(element, "background-rgb", d=(255, 255, 255, 150)),
            major_annotation_colour=colour_attr(element, "major-ann-rgb", d=(0, 0, 0)),
            minor_annotation_colour=colour_attr(element, "minor-ann-rgb", d=(0, 0, 0)),
            major_tick_colour=colour_attr(element, "major-tick-rgb", d=(0, 0, 0)),
            minor_tick_colour=colour_attr(element, "minor-tick-rgb", d=(0, 0, 0)),
            v_min=min_value,
            v_max=max_value,
            needle_colour=colour_attr(element, "needle-rgb", d=(255, 0, 0))
        )
    )


@allow_attributes({"size", "min", "max", "metric", "units", "start", "length",
                   "sectors",
                   "background-rgb",
                   "major-ann-rgb", "minor-ann-rgb",
                   "major-tick-rgb", "minor-tick-rgb",
                   "needle-rgb",
                   "arc-inner-rgb", "arc-outer-rgb",
                   "arc-metric-upper", "arc-metric-lower",
                   "arc-value-upper", "arc-value-lower"
                   })
def create_cairo_gauge_arc_annotated(element, entry, converters, **kwargs) -> Widget:
    size = iattrib(element, "size", d=256)

    min_value = iattrib(element, "min", d=0)
    max_value = iattrib(element, "max", d=50)

    converter = converters.converter(attrib(element, "units", d=None))

    def a_metric(attr_name):
        return metric_value(
            entry,
            accessor=metric_accessor_from(attrib(element, attr_name)),
            converter=converter,
            formatter=lambda q: q.m,
            default=0
        )

    if "arc-metric-lower" in element.attrib:
        reading_arc_lower = a_metric("arc-metric-lower")
    elif "arc-value-lower" in element.attrib:
        lower_value = fattrib(element, "arc-value-lower")
        reading_arc_lower = as_reading(lambda: lower_value, min_value, max_value)
    else:
        reading_arc_lower = as_reading(lambda: 0, min_value, max_value)

    if "arc-metric-upper" in element.attrib:
        reading_arc_upper = a_metric("arc-metric-upper")
    elif "arc-value-upper" in element.attrib:
        upper_value = fattrib(element, "arc-value-upper")
        reading_arc_upper = as_reading(lambda: upper_value, min_value, max_value)
    else:
        reading_arc_upper = None

    return CairoAdapter(
        size=Dimension(size, size),
        widget=CairoGaugeSectorAnnotated(
            start=Angle(degrees=iattrib(element, "start", d=143)),
            length=Angle(degrees=iattrib(element, "length", d=254)),
            sectors=iattrib(element, "sectors", d=5),
            background_colour=colour_attr(element, "background-rgb", d=(255, 255, 255, 150)),
            major_annotation_colour=colour_attr(element, "major-ann-rgb", d=(0, 0, 0)),
            minor_annotation_colour=colour_attr(element, "minor-ann-rgb", d=(0, 0, 0)),
            major_tick_colour=colour_attr(element, "major-tick-rgb", d=(0, 0, 0)),
            minor_tick_colour=colour_attr(element, "minor-tick-rgb", d=(0, 0, 0)),
            v_min=min_value,
            v_max=max_value,
            reading=as_reading(a_metric("metric"), min_value, max_value),
            needle_colour=colour_attr(element, "needle-rgb", d=(255, 0, 0)),
            arc_inner_colour=colour_attr(element, "arc-inner-rgb", d=(0, 0, 190, 50)),
            arc_outer_colour=colour_attr(element, "arc-outer-rgb", d=(0, 0, 190, 190)),
            reading_arc_max=reading_arc_upper,
            reading_arc_min=reading_arc_lower
        )
    )

@allow_attributes({"size", "min", "max", "metric", "units", "start", "length",
                   "sectors",
                   "background-inner-rgb", "background-outer-rgb",
                   "major-ann-rgb", "minor-ann-rgb",
                   "major-tick-rgb", "minor-tick-rgb",
                   "needle-rgb",
                   "arc-inner-rgb", "arc-outer-rgb",
                   "arc-metric-upper", "arc-metric-lower",
                   "arc-value-upper", "arc-value-lower"
                   })
def create_cairo_gauge_donut(element, entry, converters, **kwargs) -> Widget:
    size = iattrib(element, "size", d=256)

    min_value = iattrib(element, "min", d=0)
    max_value = iattrib(element, "max", d=50)

    converter = converters.converter(attrib(element, "units", d=None))

    def a_metric(attr_name):
        return metric_value(
            entry,
            accessor=metric_accessor_from(attrib(element, attr_name)),
            converter=converter,
            formatter=lambda q: q.m,
            default=0
        )

    if "arc-metric-lower" in element.attrib:
        reading_arc_lower = a_metric("arc-metric-lower")
    elif "arc-value-lower" in element.attrib:
        lower_value = fattrib(element, "arc-value-lower")
        reading_arc_lower = as_reading(lambda: lower_value, min_value, max_value)
    else:
        reading_arc_lower = as_reading(lambda: 0, min_value, max_value)

    if "arc-metric-upper" in element.attrib:
        reading_arc_upper = a_metric("arc-metric-upper")
    elif "arc-value-upper" in element.attrib:
        upper_value = fattrib(element, "arc-value-upper")
        reading_arc_upper = as_reading(lambda: upper_value, min_value, max_value)
    else:
        reading_arc_upper = None

    return CairoAdapter(
        size=Dimension(size, size),
        widget=CairoGaugeDonutAnnotated(
            start=Angle(degrees=iattrib(element, "start", d=143)),
            length=Angle(degrees=iattrib(element, "length", d=254)),
            sectors=iattrib(element, "sectors", d=5),
            background_inner=colour_attr(element, "background-inner-rgb", d=(255, 255, 255, 150)),
            background_outer=colour_attr(element, "background-inner-rgb", d=(255, 255, 255, 255)),
            major_annotation_colour=colour_attr(element, "major-ann-rgb", d=(0, 0, 0)),
            minor_annotation_colour=colour_attr(element, "minor-ann-rgb", d=(0, 0, 0)),
            major_tick_colour=colour_attr(element, "major-tick-rgb", d=(0, 0, 0)),
            minor_tick_colour=colour_attr(element, "minor-tick-rgb", d=(0, 0, 0)),
            v_min=min_value,
            v_max=max_value,
            reading=as_reading(a_metric("metric"), min_value, max_value),
            needle_colour=colour_attr(element, "needle-rgb", d=(255, 0, 0)),
            arc_inner_colour=colour_attr(element, "arc-inner-rgb", d=(0, 0, 190, 50)),
            arc_outer_colour=colour_attr(element, "arc-outer-rgb", d=(0, 0, 190, 190)),
            reading_arc_max=reading_arc_upper,
            reading_arc_min=reading_arc_lower
        )
    )
