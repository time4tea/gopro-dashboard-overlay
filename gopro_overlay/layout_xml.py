import sys
import xml.etree.ElementTree as ET

from gopro_overlay.layout_components import date_and_time, gps_info, moving_map, journey_map, big_mph, gradient, \
    temperature, cadence, heartbeat, gradient_chart, text, metric, text_dynamic
from gopro_overlay.point import Coordinate
from gopro_overlay.units import units
from gopro_overlay.widgets import simple_icon


def layout_from_xml(xml, renderer, timeseries, font, privacy):
    root = ET.fromstring(xml)

    fonts = {}

    def font_at(size):
        return fonts.setdefault(size, font.font_variant(size=size))

    def create(entry):
        def create_component(child):
            if not child.tag == "component":
                raise ValueError(f"Was expecting 'component' element, not '{child.tag}'")
            component_type = child.attrib["type"]

            attr = f"create_{component_type}"

            if not hasattr(sys.modules[__name__], attr):
                raise IOError(f"Component of type of '{component_type}' is not recognised, check spelling / examples")

            method = getattr(sys.modules[__name__], attr)
            return method(child, entry=entry, renderer=renderer, timeseries=timeseries, font=font_at, privacy=privacy)

        return [create_component(child) for child in root]

    return create


def attrib(el, a, f=lambda v: v, **kwargs):
    if a not in el.attrib:
        if "d" in kwargs:
            return kwargs["d"]
        raise ValueError(f"Was expecting element '{el.tag}' to have attribute '{a}', but it does not")
    return f(el.attrib[a])


def iattrib(el, a, d=None, r=None):
    v = attrib(el, a, f=int, d=d)
    if r:
        if v not in r:
            raise ValueError(f"Value for '{a}' in '{el.tag}' needs to lie in range {r.start} to {r.stop}, not '{v}'")
    return v


def battrib(el, a, d):
    return attrib(el, a, f=bool, d=d)


def at(el):
    return Coordinate(iattrib(el, "x"), iattrib(el, "y"))


def metric_accessor_from(name):
    accessors = {
        "hr": lambda e: e.hr,
        "speed": lambda e: e.speed,
        "temp": lambda e: e.atemp,
        "gradient": lambda e: e.grad,
        "alt": lambda e: e.alt,
        "odo": lambda e: e.odo,
        "dist": lambda e: e.dist,
        "azi": lambda e: e.azi,
        "lat": lambda e: units.Quantity(e.point.lat, units.location),
        "lon": lambda e: units.Quantity(e.point.lon, units.location),
    }
    if name in accessors:
        return accessors[name]
    raise IOError(f"The metric '{name}' is not supported. Use one of: {accessors.keys()}")


def metric_converter_from(name):
    if name is None:
        return lambda x: x
    converters = {
        "mph": lambda u: u.to("MPH"),
        "kph": lambda u: u.to("KPH"),
        "mps": lambda u: u.to("mps"),
        "knots": lambda u: u.to("knot"),

        "feet": lambda u: u.to("international_feet"),
        "miles": lambda u: u.to("mile"),
        "nautical_miles": lambda u: u.to("nautical_mile"),
    }
    if name in converters:
        return converters[name]
    raise IOError(f"The conversion '{name}' is not supported. Use one of: {converters.keys()}")


def formatter_from(element):
    format_string = attrib(element, "format", d=None)
    dp = attrib(element, "dp", d=None)

    if format_string and dp:
        raise IOError("Cannot supply both 'format' and 'dp', just use one")

    if format_string:
        return lambda v: format(v, format_string)
    if dp:
        return lambda v: format(v, f".{dp}f")


def create_metric(element, entry, font, **kwargs):
    return metric(
        at=at(element),
        entry=entry,
        accessor=metric_accessor_from(attrib(element, "metric")),
        formatter=formatter_from(element),
        font=font(iattrib(element, "size", d=16)),
        converter=metric_converter_from(attrib(element, "units", d=None)),
        align=attrib(element, "align", d="left"),
        cache=battrib(element, "cache", d=True),
    )


def create_icon(element, **kwargs):
    return simple_icon(
        at=at(element),
        file=attrib(element, "file"),
        size=iattrib(element, "size", d=64)
    )


def date_formatter_from(element, entry):
    format_string = attrib(element, "format")
    truncate = iattrib(element, "truncate", d=0)

    if truncate > 0:
        return lambda: entry().dt.strftime(format_string)[:-truncate]
    else:
        return lambda: entry().dt.strftime(format_string)


def create_datetime(element, entry, font, **kwargs):
    return text_dynamic(
        at(element),
        date_formatter_from(element, entry),
        font=font(iattrib(element, "size", d=16)),
        align=attrib(element, "align", d="left"),
        cache=battrib(element, "cache", d=True)
    )


def create_text(element, font, **kwargs):
    if element.text is None:
        raise IOError("Text components should have the text in the element like <component...>Text</component>")

    return text(
        at(element),
        element.text,
        font=font(iattrib(element, "size", d=16)),
        align=attrib(element, "align", d="left")
    )


def create_date_and_time(element, entry, font, **kwargs):
    font_title = font(iattrib(element, "size_date", d=16))
    font_metric = font(iattrib(element, "size_time", d=32))

    return date_and_time(at(element), entry=entry, font_title=font_title, font_metric=font_metric)


def create_gps_info(element, entry, font, **kwargs):
    return gps_info(at(element), entry=entry, font=font(iattrib(element, "size", d=16)))


def create_moving_map(element, entry, renderer, **kwargs):
    return moving_map(
        at(element),
        entry,
        size=iattrib(element, "size", d=256),
        zoom=iattrib(element, "zoom", d=16, r=range(1, 18)),
        renderer=renderer
    )


def create_journey_map(element, entry, privacy, renderer, timeseries, **kwargs):
    return journey_map(
        at(element),
        entry,
        privacy,
        renderer,
        timeseries,
        size=iattrib(element, "size", d=256)
    )


def create_big_mph(element, entry, font, **kwargs):
    return big_mph(
        at(element),
        entry,
        font_title=font(iattrib(element, "size_title", d=16)),
        font_metric=font(iattrib(element, "size_metric", d=160))
    )


def create_gradient(element, entry, font, **kwargs):
    return gradient(
        at(element),
        entry,
        font_title=font(iattrib(element, "size_title", d=16)),
        font_metric=font(iattrib(element, "size_metric", d=32))
    )


def create_temperature(element, entry, font, **kwargs):
    return temperature(
        at(element),
        entry,
        font_title=font(iattrib(element, "size_title", d=16)),
        font_metric=font(iattrib(element, "size_metric", d=32))
    )


def create_cadence(element, entry, font, **kwargs):
    return cadence(
        at(element),
        entry,
        font_title=font(iattrib(element, "size_title", d=16)),
        font_metric=font(iattrib(element, "size_metric", d=32))
    )


def create_heartbeat(element, entry, font, **kwargs):
    return heartbeat(
        at(element),
        entry,
        font_title=font(iattrib(element, "size_title", d=16)),
        font_metric=font(iattrib(element, "size_metric", d=32))
    )


def create_gradient_chart(element, entry, timeseries, font, **kwargs):
    return gradient_chart(
        at(element),
        timeseries,
        entry,
        font_title=font(iattrib(element, "size_title", d=16))
    )
