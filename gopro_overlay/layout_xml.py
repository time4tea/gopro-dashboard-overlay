import sys
import xml.etree.ElementTree as ET

from gopro_overlay.layout_components import date_and_time, gps_info, moving_map, journey_map, big_mph, gradient, \
    temperature, cadence, heartbeat, gradient_chart
from gopro_overlay.point import Coordinate


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
            method = getattr(sys.modules[__name__], f"create_{component_type}")
            return method(child, entry=entry, renderer=renderer, timeseries=timeseries, font=font_at, privacy=privacy)

        return [create_component(child) for child in root]

    return create


def attrib(el, a, f=lambda v: v, d=None):
    if a not in el.attrib:
        if d is not None:
            return d
        raise ValueError(f"Was expecting element {el.tag} to have attribute {a}, but it does not")
    return f(el.attrib[a])


def iattrib(el, a, d=None, r=None):
    v = attrib(el, a, f=int, d=d)
    if r:
        if v not in r:
            raise ValueError(f"Value for {a} in {el.tag} needs to lie in range {r.start} to {r.stop}, not {v}")
    return v


def at(el):
    return Coordinate(int(attrib(el, "x")), int(attrib(el, "y")))


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
