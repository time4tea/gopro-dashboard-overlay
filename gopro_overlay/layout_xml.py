import importlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Optional

import pint
from pint.formatting import format_unit

from gopro_overlay import layouts
from gopro_overlay.dimensions import Dimension
from gopro_overlay.framemeta import Window
from gopro_overlay.layout_components import moving_map, journey_map, text, metric, metric_value
from gopro_overlay.point import Coordinate
from gopro_overlay.timeseries import Entry
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units
from .log import log
from .widgets.asi import AirspeedIndicator
from .widgets.bar import Bar
from .widgets.chart import SimpleChart
from .widgets.compass import Compass
from .widgets.compass_arrow import CompassArrow
from .widgets.gps import GPSLock
from .widgets.map import MovingJourneyMap, Circuit
from .widgets.profile import WidgetProfiler
from .widgets.widgets import simple_icon, Translate, Composite, Frame, Widget
from .widgets.gradient_bar import GradientBar

def load_xml_layout(filepath: Path):
    if filepath.exists():
        with filepath.open() as f:
            return f.read()

    with importlib.resources.path(layouts, f"{filepath.name}.xml") as fn:
        with open(fn) as f:
            return f.read()


class Converters:

    def __init__(self, speed_unit="mph", distance_unit="mile", altitude_unit="m", temperature_unit="degC"):
        self.speed_unit = speed_unit
        self.distance_unit = distance_unit
        self.altitude_unit = altitude_unit
        self.temperature_unit = temperature_unit

    def converter(self, name):
        if name is None:
            return lambda x: x
        converters = {
            # speed
            "mph": lambda u: u.to("MPH"),
            "kph": lambda u: u.to("KPH"),
            "knots": lambda u: u.to("knot"),

            # User selectable
            "speed": lambda u: u.to(self.speed_unit),
            "distance": lambda u: u.to(self.distance_unit),

            "altitude": lambda u: u.to(self.altitude_unit),
            "alt": lambda u: u.to(self.altitude_unit),

            "temp": lambda u: u.to(self.temperature_unit),
            "temperature": lambda u: u.to(self.temperature_unit),

            # accel
            "G": lambda u: u.to("gravity"),

            # alt / dist
            "feet": lambda u: u.to("international_feet"),
            "miles": lambda u: u.to("mile"),
            "metres": lambda u: u.to("m"),
            "nautical_miles": lambda u: u.to("nautical_mile"),
        }
        if name in converters:
            return converters[name]

        # Try to see if specified unit is recognised by pint... if so allow it - this only means its a valid
        # unit, but actual metric might be different... if unconvertible it will blow up later...
        try:
            units.Quantity(1, units=name)
            return lambda u: u.to(name)
        except Exception as e:
            raise IOError(f"The conversion '{name}' is not supported.")


def layout_from_xml(xml, renderer, framemeta, font, privacy, include=lambda name: True,
                    decorator: Optional[WidgetProfiler] = None, converters: Converters = Converters()):
    root = ET.fromstring(xml)

    fonts = {}

    def font_at(size):
        return fonts.setdefault(size, font.font_variant(size=size))

    factory = Widgets(
        font=font_at,
        privacy=privacy,
        renderer=renderer,
        framemeta=framemeta,
        converters=converters,
    )

    def name_of(element):
        return attrib(element, "name", d=None)

    def want_element(element):
        name = name_of(element)
        if name is not None:
            b = include(name)
            log(f"Layout -> Include component '{name}' = {b}")
            return b
        return True

    def decorate(name, level, widget):
        if decorator:
            class_name = widget.__class__.__name__
            name = f"{class_name} - {name}" if name else class_name

            return decorator.decorate(name, level, widget)
        else:
            return widget

    def create(entry):
        def create_component(child, level):
            component_type = child.attrib["type"].replace("-", "_")

            attr = f"create_{component_type}"

            if not hasattr(factory, attr):
                raise IOError(f"Component of type of '{component_type}' is not recognised, check spelling / examples")

            method = getattr(factory, attr)
            return decorate(
                name=name_of(child),
                level=level,
                widget=method(child, entry=entry)
            )

        def create_composite(element, level):
            return decorate(
                name=name_of(element),
                level=level,
                widget=Translate(
                    at(element),
                    Composite(
                        *[do_element(child, level + 1) for child in element if want_element(child)]
                    )
                )
            )

        def create_frame(element, level):
            return decorate(
                name=name_of(element),
                level=level,
                widget=Translate(
                    at(element),
                    Frame(
                        dimensions=Dimension(x=iattrib(element, "width"), y=iattrib(element, "height")),
                        opacity=fattrib(element, "opacity", d=1.0),
                        corner_radius=iattrib(element, "cr", d=0),
                        outline=rgbattr(element, "outline", None),
                        fill=rgbattr(element, "bg", d=None),
                        fade_out=iattrib(element, "fo", d=0),
                        child=Composite(
                            *[do_element(child, level + 1) for child in element if want_element(child)]
                        )
                    )
                )
            )

        def do_element(element, level):
            elements = {
                "composite": create_composite,
                "translate": create_composite,
                "component": create_component,
                "frame": create_frame,
            }
            if element.tag not in elements:
                raise IOError(f"Tag {element.tag} is not recognised. Should be one of '{list(elements.keys())}'")

            return elements[element.tag](element, level)

        try:
            return [decorate(
                name="ROOT",
                level=0,
                widget=Composite(
                    *[do_element(child, 1) for child in root if want_element(child)]
                )
            )]
        except ValueError as e:
            raise IOError(e)

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
    if len(v) != 3 and len(v) != 4:
        raise ValueError(
            f"RGB value for '{a}' in '{el.tag}' needs to be 3 numbers (r,g,b), or 4 (r,g,b,a) not {len(v)}")
    return v


def at(el):
    return Coordinate(iattrib(el, "x", d=0), iattrib(el, "y", d=0))


def metric_accessor_from(name):
    accessors = {
        "hr": lambda e: e.hr,
        "cadence": lambda e: e.cad,
        "power": lambda e: e.power,
        "speed": lambda e: e.speed if e.speed is not None else e.cspeed,
        "cspeed": lambda e: e.cspeed,
        "temp": lambda e: e.atemp,
        "gradient": lambda e: e.grad if e.grad is not None else e.cgrad,
        "cgrad": lambda e: e.cgrad,
        "alt": lambda e: e.alt,
        "odo": lambda e: e.odo if e.odo is not None else e.codo,
        "codo": lambda e: e.codo,
        "dist": lambda e: e.dist,
        "azi": lambda e: e.azi,
        "cog": lambda e: e.cog,

        "gps-dop": lambda e: e.dop,
        "timestamp": lambda e: e.timestamp,
        "gps-packet": lambda e: e.packet,
        "gps-packet-index": lambda e: e.packet_index,
        "gps-lock": lambda e: e.gpslock,

        "accl.x": lambda e: e.accl.x if e.accl else None,
        "accl.y": lambda e: e.accl.y if e.accl else None,
        "accl.z": lambda e: e.accl.z if e.accl else None,
        "grav.x": lambda e: e.grav.x if e.grav else None,
        "grav.y": lambda e: e.grav.y if e.grav else None,
        "grav.z": lambda e: e.grav.z if e.grav else None,
        "ori.pitch": lambda e: e.ori.pitch if e.ori else None,
        "ori.roll": lambda e: e.ori.roll if e.ori else None,
        "ori.yaw": lambda e: e.ori.yaw if e.ori else None,
        "lat": lambda e: units.Quantity(e.point.lat, units.location),
        "lon": lambda e: units.Quantity(e.point.lon, units.location),
    }
    if name in accessors:
        return accessors[name]
    raise IOError(f"The metric '{name}' is not supported. Use one of: {list(accessors.keys())}")


def quantity_formatter_from(element) -> Callable[[pint.Quantity], str]:
    format_string = attrib(element, "format", d=None)
    dp = attrib(element, "dp", d=None)

    if format_string and dp:
        raise IOError("Cannot supply both 'format' and 'dp', just use one")

    if format_string is None and dp is None:
        dp = 2

    if format_string:
        try:
            return lambda q: format(q.m, format_string)
        except ValueError:
            raise ValueError(f"Unable to format value with format string {format_string}")
    if dp:
        return lambda q: format(q.m, f".{dp}f")


def date_formatter_from(entry: Callable[[], Entry], format_string, truncate=0, tz=None) -> Callable[[], str]:
    if truncate > 0:
        return lambda: entry().dt.astimezone(tz=tz).strftime(format_string)[:-truncate]
    else:
        return lambda: entry().dt.astimezone(tz=tz).strftime(format_string)


def date_formatter_from_element(element, entry: Callable[[], Entry]):
    format_string = attrib(element, "format")
    truncate = iattrib(element, "truncate", d=0)

    return date_formatter_from(entry, format_string, truncate)


def nonesafe(v):
    if v is not None:
        return v.magnitude
    else:
        return 0


@pint.register_unit_format("c")
def format_uppercase(unit, registry, **options):
    return format_unit(unit, "C", registry).upper()


@pint.register_unit_format("p")
def format_uppercase(unit, registry, **options):
    return format_unit(unit, "P", registry).upper()


@pint.register_unit_format("d")
def format_uppercase(unit, registry, **options):
    return format_unit(unit, "D", registry).upper()


class Widgets:

    def __init__(self, font, privacy, renderer, framemeta, converters):
        self.framemeta = framemeta
        self.renderer = renderer
        self.privacy = privacy
        self.font = font
        self.converters = converters

    def create_metric(self, element, entry, **kwargs) -> Widget:
        return metric(
            at=at(element),
            entry=entry,
            accessor=metric_accessor_from(attrib(element, "metric")),
            formatter=quantity_formatter_from(element),
            font=self.font(iattrib(element, "size", d=16)),
            converter=self.converters.converter(attrib(element, "units", d=None)),
            align=attrib(element, "align", d="left"),
            cache=battrib(element, "cache", d=True),
            fill=rgbattr(element, "rgb", d=(255, 255, 255)),
            stroke=rgbattr(element, "outline", d=(0, 0, 0)),
            stroke_width=iattrib(element, "outline_width", d=2),
        )

    def create_metric_unit(self, element, entry, **kwargs) -> Widget:

        format_string = element.text or "{:~C}"

        return metric(
            at=at(element),
            entry=entry,
            accessor=metric_accessor_from(attrib(element, "metric")),
            formatter=lambda q: format_string.format(q.u),
            font=self.font(iattrib(element, "size", d=16)),
            converter=self.converters.converter(attrib(element, "units", d=None)),
            align=attrib(element, "align", d="left"),
            cache=True,
            fill=rgbattr(element, "rgb", d=(255, 255, 255)),
            stroke=rgbattr(element, "outline", d=(0, 0, 0)),
            stroke_width=iattrib(element, "outline_width", d=2),
        )

    def create_icon(self, element, **kwargs) -> Widget:
        return simple_icon(
            at=at(element),
            file=attrib(element, "file"),
            size=iattrib(element, "size", d=64),
            invert=battrib(element, "invert", d=True)
        )

    def create_datetime(self, element, entry, **kwargs):
        return text(
            at=at(element),
            value=date_formatter_from_element(element, entry),
            font=self.font(iattrib(element, "size", d=16)),
            align=attrib(element, "align", d="left"),
            cache=battrib(element, "cache", d=True),
            fill=rgbattr(element, "rgb", d=(255, 255, 255))
        )

    def create_text(self, element, entry, **kwargs) -> Widget:
        if element.text is None:
            raise IOError("Text components should have the text in the element like <component...>Text</component>")

        return text(
            at=at(element),
            value=lambda: element.text,
            font=self.font(iattrib(element, "size", d=16)),
            align=attrib(element, "align", d="left"),
            direction=attrib(element, "direction", d="ltr"),
            fill=rgbattr(element, "rgb", d=(255, 255, 255)),
            stroke=rgbattr(element, "outline", d=(0, 0, 0)),
            stroke_width=iattrib(element, "outline_width", d=2),
        )

    def create_moving_map(self, element, entry, **kwargs) -> Widget:
        return moving_map(
            at=at(element),
            entry=entry,
            size=iattrib(element, "size", d=256),
            zoom=iattrib(element, "zoom", d=16, r=range(1, 20)),
            renderer=self.renderer,
            corner_radius=iattrib(element, "corner_radius", 0),
            opacity=fattrib(element, "opacity", 0.7),
            rotate=battrib(element, "rotate", d=True)
        )

    def create_journey_map(self, element, entry, **kwargs) -> Widget:
        return journey_map(
            at(element),
            entry,
            privacy_zone=self.privacy,
            renderer=self.renderer,
            timeseries=self.framemeta,
            size=iattrib(element, "size", d=256),
            corner_radius=iattrib(element, "corner_radius", 0),
            opacity=fattrib(element, "opacity", 0.7)
        )

    def create_moving_journey_map(self, element, entry, **kwargs) -> Widget:
        return MovingJourneyMap(
            location=lambda: entry().point,
            privacy_zone=self.privacy,
            renderer=self.renderer,
            timeseries=self.framemeta,
            size=iattrib(element, "size", d=256),
            zoom=iattrib(element, "zoom", d=16, r=range(1, 20))
        )

    def create_circuit_map(self, element, entry, **kwargs) -> Widget:
        size = iattrib(element, "size", d=256)
        return Circuit(
            location=lambda: entry().point,
            privacy_zone=self.privacy,
            framemeta=self.framemeta,
            dimensions=Dimension(size, size),
            fill=rgbattr(element, "fill", d=(255, 0, 0)),
            outline=rgbattr(element, "outline", d=(255, 255, 255)),
            fill_width=iattrib(element, "fill_width", d=4),
            outline_width=iattrib(element, "outline_width", d=0)
        )

    def create_gradient_chart(self, *args, **kwargs):
        log("Use of component `gradient_chart` is now deprecated - please use `chart` instead.")
        return self.create_chart(*args, **kwargs)

    def create_chart(self, element, entry, **kwargs) -> Widget:
        accessor = metric_accessor_from(attrib(element, "metric", d="alt"))
        converter = self.converters.converter(attrib(element, "units", d="metres"))

        def value(e):
            v = accessor(e)
            if v is not None:
                v = converter(v)
                return v.magnitude
            return None

        window = Window(
            self.framemeta,
            duration=timeunits(seconds=iattrib(element, "seconds", d=5 * 60)),
            samples=iattrib(element, "samples", d=256),
            key=value
        )

        title = self.font(iattrib(element, "size_title", d=16))
        values = battrib(element, "values", d=True)
        if not values:
            title = None

        return Translate(
            at=at(element),
            widget=SimpleChart(
                value=lambda: window.view(timeunits(millis=entry().timestamp.magnitude)),
                font=title,
                filled=battrib(element, "filled", d=True),
                height=iattrib(element, "height", d=64),
                bg=rgbattr(element, "bg", d=(0, 0, 0, 170)),
                fill=rgbattr(element, "fill", d=(91, 113, 146)),
                line=rgbattr(element, "line", d=(255, 255, 255)),
                text=rgbattr(element, "text", d=(255, 255, 255)),
                alpha=iattrib(element, "alpha", d=179, r=range(0, 256)),
            )
        )

    def create_compass(self, element, entry, **kwargs) -> Widget:
        return Compass(
            size=iattrib(element, "size", d=256),
            reading=lambda: nonesafe(entry().cog),
            font=self.font(iattrib(element, "textsize", d=16)),
            fg=rgbattr(element, "fg", d=(255, 255, 255)),
            bg=rgbattr(element, "bg", d=None),
            text=rgbattr(element, "text", d=(255, 255, 255)),
        )

    def create_compass_arrow(self, element, entry, **kwargs) -> Widget:
        return CompassArrow(
            size=iattrib(element, "size", d=256),
            reading=lambda: nonesafe(entry().cog),
            font=self.font(iattrib(element, "textsize", d=32)),
            arrow=rgbattr(element, "arrow", d=(255, 255, 255)),
            bg=rgbattr(element, "bg", d=(0, 0, 0, 0)),
            text=rgbattr(element, "text", d=(255, 255, 255)),
            outline=rgbattr(element, "outline", d=(0, 0, 0)),
            arrow_outline=rgbattr(element, "arrow_outline", d=(0, 0, 0)),
        )

    def create_bar(self, element, entry, **kwargs) -> Widget:
        return Bar(
            size=Dimension(x=iattrib(element, "width", d=400), y=iattrib(element, "height", d=30)),
            reading=metric_value(
                entry,
                accessor=metric_accessor_from(attrib(element, "metric")),
                converter=self.converters.converter(attrib(element, "units", d=None)),
                formatter=lambda q: q.m,
                default=0
            ),
            fill=rgbattr(element, "fill", d=(255, 255, 255, 0)),
            zero=rgbattr(element, "zero", d=(255, 255, 255)),
            bar=rgbattr(element, "bar", d=(255, 255, 255)),
            outline=rgbattr(element, "outline", d=(255, 255, 255)),
            outline_width=iattrib(element, "outline-width", d=3),
            highlight_colour_negative=rgbattr(element, "h-neg", d=(255, 0, 0)),
            highlight_colour_positive=rgbattr(element, "h-pos", d=(0, 255, 0)),
            max_value=iattrib(element, "max", d=20),
            min_value=iattrib(element, "min", d=-20),
            cr=iattrib(element, "cr", d=5),
        )

    def create_zone_bar(self, element, entry, **kwargs):
        return GradientBar(
            size=Dimension(x=iattrib(element, "width", d=400), y=iattrib(element, "height", d=30)),
            reading=metric_value(
                entry,
                accessor=metric_accessor_from(attrib(element, "metric")),
                converter=self.converters.converter(attrib(element, "units", d=None)),
                formatter=lambda q: q.m,
                default=0
            ),
            fill=rgbattr(element, "fill", d=(255, 255, 255, 0)),
            divider=rgbattr(element, "zone-divider", d=(255, 255, 255)),
            outline=rgbattr(element, "outline", d=(255, 255, 255)),
            outline_width=iattrib(element, "outline-width", d=3),
            cr=iattrib(element, "cr", d=5),
            max_value=iattrib(element, "max", d=1000),
            min_value=iattrib(element, "min", d=0),
            z1_value=iattrib(element, "z1", d=120),
            z2_value=iattrib(element, "z2", d=160),
            z3_value=iattrib(element, "z3", d=200),
            z0_color=rgbattr(element, "z0-color", d=(255, 255, 255)),
            z1_color=rgbattr(element, "z1-color", d=(67, 235, 52)),
            z2_color=rgbattr(element, "z2-color", d=(240, 232, 19)),
            z3_color=rgbattr(element, "z3-color", d=(207, 19, 2)),
        )


    def create_asi(self, element, entry, **kwargs) -> Widget:
        return AirspeedIndicator(
            size=iattrib(element, "size", d=256),
            reading=metric_value(
                entry,
                accessor=metric_accessor_from(attrib(element, "metric", d="speed")),
                converter=self.converters.converter(attrib(element, "units", d="knots")),
                formatter=lambda q: q.m,
                default=0
            ),
            font=self.font(iattrib(element, "textsize", d=16)),
            Vs0=iattrib(element, "vs0", d=40),
            Vs=iattrib(element, "vs", d=46),
            Vfe=iattrib(element, "vfe", d=103),
            Vno=iattrib(element, "vno", d=126),
            Vne=iattrib(element, "vne", d=180),
            rotate=iattrib(element, "rotate", d=0),
        )

    def create_cairo_circuit_map(self, element, entry, **kwargs):
        try:
            import gopro_overlay.layout_xml_cairo
            return gopro_overlay.layout_xml_cairo.create_cairo_circuit_map(element, entry, self.framemeta, **kwargs)
        except ModuleNotFoundError:
            raise IOError("This widget needs pycairo to be installed - please see docs") from None

    def create_gps_lock_icon(self, element, entry, **kwargs) -> Widget:
        at = Coordinate(0, 0)
        size = iattrib(element, "size", d=64)
        return GPSLock(
            fix=lambda: entry().gpsfix,
            lock_no=simple_icon(at, attrib(element, "lock_none", d="gps_lock_none.png"), size),
            lock_unknown=simple_icon(at, attrib(element, "lock_unknown", d="gps_lock_unknown.png"), size),
            lock_2d=simple_icon(at, attrib(element, "lock_2d", d="gps_lock_2d.png"), size),
            lock_3d=simple_icon(at, attrib(element, "lock_3d", d="gps_lock_3d.png"), size),
        )
