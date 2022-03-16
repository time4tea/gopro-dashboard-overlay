import importlib
import os.path
import sys
import xml.etree.ElementTree as ET
from typing import Callable

from gopro_overlay import layouts
from gopro_overlay.dimensions import Dimension
from gopro_overlay.layout_components import moving_map, journey_map, gradient_chart, \
    text, metric, metric_value
from gopro_overlay.point import Coordinate
from gopro_overlay.timeseries import Entry
from gopro_overlay.units import units
from gopro_overlay.widgets import simple_icon, Translate, Composite, Frame
from gopro_overlay.widgets_asi import AirspeedIndicator
from gopro_overlay.widgets_compass import Compass


def load_xml_layout(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            return f.read()

    with importlib.resources.path(layouts, f"{filename}.xml") as fn:
        with open(fn) as f:
            return f.read()


def layout_from_xml(xml, renderer, timeseries, font, privacy, include=lambda name: True):
    root = ET.fromstring(xml)

    fonts = {}

    def font_at(size):
        return fonts.setdefault(size, font.font_variant(size=size))

    def want_element(element):
        name = attrib(element, "name", d=None)
        if name is not None:
            return include(name)
        return True

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

        def create_composite(element):
            return Translate(
                at(element),
                Composite(
                    *[do_element(child) for child in element if want_element(child)]
                )
            )

        def create_frame(element):
            return Translate(
                at(element),
                Frame(
                    dimensions=Dimension(x=iattrib(element, "width"), y=iattrib(element, "height")),
                    opacity=fattrib(element, "opacity", d=1.0),
                    corner_radius=iattrib(element, "cr", d=0),
                    outline=rgbattr(element, "outline", None),
                    fill=rgbattr(element, "bg", d=None),
                    child=Composite(
                        *[do_element(child) for child in element if want_element(child)]
                    )
                )
            )

        def do_element(element):
            elements = {
                "composite": create_composite,
                "translate": create_composite,
                "component": create_component,
                "frame": create_frame,
            }
            if element.tag not in elements:
                raise IOError(f"Tag {element.tag} is not recognised. Should be one of '{list(elements.keys())}'")

            return elements[element.tag](element)

        return [do_element(child) for child in root if want_element(child)]

    return create


def attrib(el, a, f=lambda v: v, **kwargs):
    """Use kwargs so can return a default value of None"""
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


def fattrib(el, a, d=None, r=None):
    v = attrib(el, a, f=float, d=d)
    if r:
        if v not in r:
            raise ValueError(f"Value for '{a}' in '{el.tag}' needs to lie in range {r.start} to {r.stop}, not '{v}'")
    return v


def battrib(el, a, d):
    return attrib(el, a, f=lambda s: s.lower() in ["true", "yes", "1"], d=d)


def rgbattr(el, a, d):
    v = attrib(el, a, f=lambda s: tuple(map(int, s.split(","))), d=d)
    if v is None:
        return v
    if len(v) != 3:
        raise ValueError(f"RGB value for '{a}' in '{el.tag}' needs to be 3 numbers (r,g,b), not {len(v)}")
    return v


def at(el):
    return Coordinate(iattrib(el, "x", d=0), iattrib(el, "y", d=0))


def metric_accessor_from(name):
    accessors = {
        "hr": lambda e: e.hr,
        "cadence": lambda e: e.cad,
        "speed": lambda e: e.speed or e.cspeed,
        "cspeed": lambda e: e.cspeed,
        "temp": lambda e: e.atemp,
        "gradient": lambda e: e.grad,
        "alt": lambda e: e.alt,
        "odo": lambda e: e.odo,
        "dist": lambda e: e.dist,
        "azi": lambda e: e.azi,
        "cog": lambda e: e.cog,
        "lat": lambda e: units.Quantity(e.point.lat, units.location),
        "lon": lambda e: units.Quantity(e.point.lon, units.location),
    }
    if name in accessors:
        return accessors[name]
    raise IOError(f"The metric '{name}' is not supported. Use one of: {list(accessors.keys())}")


def metric_converter_from(name):
    if name is None:
        return lambda x: x
    converters = {
        "mph": lambda u: u.to("MPH"),
        "kph": lambda u: u.to("KPH"),
        "mps": lambda u: u.to("mps"),
        "knots": lambda u: u.to("knot"),

        "degreeF": lambda u: u.to('degreeF'),
        "degreeC": lambda u: u.to('degreeC'),

        "radian": lambda u: u.to("radian"),

        "feet": lambda u: u.to("international_feet"),
        "miles": lambda u: u.to("mile"),
        "nautical_miles": lambda u: u.to("nautical_mile"),
    }
    if name in converters:
        return converters[name]
    raise IOError(f"The conversion '{name}' is not supported. Use one of: {list(converters.keys())}")


def formatter_from(element):
    format_string = attrib(element, "format", d=None)
    dp = attrib(element, "dp", d=None)

    if format_string and dp:
        raise IOError("Cannot supply both 'format' and 'dp', just use one")

    if format_string is None and dp is None:
        dp = 2

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
        fill=rgbattr(element, "rgb", d=(255, 255, 255))
    )


def create_icon(element, **kwargs):
    return simple_icon(
        at=at(element),
        file=attrib(element, "file"),
        size=iattrib(element, "size", d=64),
        invert=battrib(element, "invert", d=True)
    )


def date_formatter_from(entry: Callable[[], Entry], format_string, truncate=0, tz=None) -> Callable[[], str]:
    if truncate > 0:
        return lambda: entry().dt.astimezone(tz=tz).strftime(format_string)[:-truncate]
    else:
        return lambda: entry().dt.astimezone(tz=tz).strftime(format_string)


def date_formatter_from_element(element, entry: Callable[[], Entry]):
    format_string = attrib(element, "format")
    truncate = iattrib(element, "truncate", d=0)

    return date_formatter_from(entry, format_string, truncate)


def create_datetime(element, entry, font, **kwargs):
    return text(
        at=at(element),
        value=date_formatter_from_element(element, entry),
        font=font(iattrib(element, "size", d=16)),
        align=attrib(element, "align", d="left"),
        cache=battrib(element, "cache", d=True),
        fill=rgbattr(element, "rgb", d=(255, 255, 255))
    )


def create_text(element, font, **kwargs):
    if element.text is None:
        raise IOError("Text components should have the text in the element like <component...>Text</component>")

    return text(
        at=at(element),
        value=lambda: element.text,
        font=font(iattrib(element, "size", d=16)),
        align=attrib(element, "align", d="left"),
        direction=attrib(element, "direction", d="ltr"),
        fill=rgbattr(element, "rgb", d=(255, 255, 255))
    )


def create_moving_map(element, entry, renderer, **kwargs):
    return moving_map(
        at=at(element),
        entry=entry,
        size=iattrib(element, "size", d=256),
        zoom=iattrib(element, "zoom", d=16, r=range(1, 18)),
        renderer=renderer,
        corner_radius=iattrib(element, "corner_radius", 0),
        opacity=fattrib(element, "opacity", 0.7),
        rotate=battrib(element, "rotate", d=True)
    )


def create_journey_map(element, entry, privacy, renderer, timeseries, **kwargs):
    return journey_map(
        at(element),
        entry,
        privacy_zone=privacy,
        renderer=renderer,
        timeseries=timeseries,
        size=iattrib(element, "size", d=256),
        corner_radius=iattrib(element, "corner_radius", 0),
        opacity=fattrib(element, "opacity", 0.7)
    )


def create_gradient_chart(element, entry, timeseries, font, **kwargs):
    return gradient_chart(
        at(element),
        timeseries,
        entry,
        font_title=font(iattrib(element, "size_title", d=16))
    )


def nonesafe(v):
    if v is not None:
        return v.magnitude
    else:
        return 0


def create_compass(element, entry, timeseries, font, **kwargs):
    return Compass(
        size=iattrib(element, "size", d=256),
        reading=lambda: nonesafe(entry().cog),
        font=font(iattrib(element, "textsize", d=16)),
        fg=rgbattr(element, "fg", d=(255, 255, 255)),
        bg=rgbattr(element, "bg", d=None),
        text=rgbattr(element, "text", d=(255, 255, 255)),
    )


def create_asi(element, entry, timeseries, font, **kwargs):
    return AirspeedIndicator(
        size=iattrib(element, "size", d=256),
        reading=metric_value(
            entry,
            accessor=metric_accessor_from(attrib(element, "metric", d="speed")),
            converter=metric_converter_from(attrib(element, "units", d="knots")),
            formatter=lambda x: x,
            default=0
        ),
        font=font(iattrib(element, "textsize", d=16)),
        Vs0=iattrib(element, "vs0", d=40),
        Vs=iattrib(element, "vs", d=46),
        Vfe=iattrib(element, "vfe", d=103),
        Vno=iattrib(element, "vno", d=126),
        Vne=iattrib(element, "vne", d=180),
        rotate=iattrib(element, "rotate", d=0),
    )
