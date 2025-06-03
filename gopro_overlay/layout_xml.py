import dataclasses
import math
import xml.etree.ElementTree as ET
from importlib.resources import files, as_file
from pathlib import Path
from typing import Callable, Optional, TypeVar, Tuple

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
from .exceptions import Defect
from .layout_xml_attribute import allow_attributes
from .log import log
from .widgets.asi import AirspeedIndicator
from .widgets.msi import MotorspeedIndicator, MotorspeedIndicator2
from .widgets.bar import Bar
from .widgets.chart import SimpleChart
from .widgets.compass import Compass
from .widgets.compass_arrow import CompassArrow
from .widgets.gps import GPSLock
from .widgets.gradient_bar import GradientBar
from .widgets.map import MovingJourneyMap, Circuit
from .widgets.profile import WidgetProfiler
from .widgets.widgets import simple_icon, Translate, Composite, Frame, Widget


def load_xml_layout(filepath: Path):
    if filepath.exists():
        with filepath.open() as f:
            return f.read()

    with as_file(files(layouts) / f"{filepath.name}.xml") as fn:
        with open(fn) as f:
            return f.read()


def zero_safe(n, f):
    if n is None or n.m < 0.0000001:
        return None
    return f(n)


class Converters:

    def __init__(self, speed_unit="mph", distance_unit="mile", altitude_unit="m", temperature_unit="degC"):

        pace_unit = "pace_mile" if distance_unit == "mile" else "pace_km"

        self.converters = {
            # speed
            "none": lambda u: u,

            "mph": lambda u: u.to("MPH"),
            "kph": lambda u: u.to("KPH"),
            "knots": lambda u: u.to("knot"),

            "pace": lambda u: zero_safe(u, lambda nz: (1 / nz).to(pace_unit)),
            "pace_mile": lambda u: zero_safe(u, lambda nz: (1 / nz).to("pace_mile")),
            "pace_km": lambda u: zero_safe(u, lambda nz: (1 / nz).to("pace_km")),
            "pace_kt": lambda u: zero_safe(u, lambda nz: (1 / nz).to("pace_kt")),

            "spm": lambda u: u.to("spm"),

            # User selectable
            "speed": lambda u: u.to(speed_unit),
            "distance": lambda u: u.to(distance_unit),

            "altitude": lambda u: u.to(altitude_unit),
            "alt": lambda u: u.to(altitude_unit),

            "temp": lambda u: u.to(temperature_unit),
            "temperature": lambda u: u.to(temperature_unit),

            # accel
            "G": lambda u: u.to("gravity"),

            # alt / dist
            "feet": lambda u: u.to("international_feet"),
            "miles": lambda u: u.to("mile"),
            "metres": lambda u: u.to("m"),
            "nautical_miles": lambda u: u.to("nautical_mile"),

            # format custom fields and metadata for components which expect a float
            "custom.float": lambda u: units.Quantity(float(u.m), units.custom) if u else None
        }

    def converter(self, name: str) -> Callable[[pint.Quantity], Optional[pint.Quantity]]:
        if name is None:
            return lambda x: x
        if name in self.converters:
            return self.converters[name]

        # Try to see if specified unit is recognised by pint... if so allow it - this only means its a valid
        # unit, but actual metric might be different... if unconvertible it will blow up later...
        try:
            units.Quantity(1, units=name)
            return lambda u: u.to(name)
        except Exception:
            raise IOError(f"The conversion '{name}' is not supported.")


def layout_from_xml(xml, renderer, framemeta, font, privacy, include=lambda name: True,
                    decorator: Optional[WidgetProfiler] = None, converters: Converters = Converters(), xml_path=None):
    root = ET.fromstring(xml)

    fonts = {}

    def font_at(size):
        if size <= 0:
            raise ValueError("font size must be positive")
        return fonts.setdefault(size, font.font_variant(size=size))

    factory = Widgets(
        font=font_at,
        privacy=privacy,
        renderer=renderer,
        framemeta=framemeta,
        converters=converters,
        xml_path=xml_path
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
            component_type = component_type_of(child)

            attr = f"create_{component_type}"

            if not hasattr(factory, attr):
                raise IOError(f"Component of type of '{component_type}' is not recognised, check spelling / examples")

            method = getattr(factory, attr)
            return decorate(
                name=name_of(child),
                level=level,
                widget=method(child, entry=entry)
            )

        @allow_attributes({"x", "y"})
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

        @allow_attributes({"x", "y", "width", "height", "opacity", "cr", "outline", "bg", "fo"})
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


def component_type_of(element):
    return element.attrib["type"].replace("-", "_")


T = TypeVar("T")


def attrib(el, a, f: Callable[[str], T] = lambda v: v, **kwargs) -> T:
    """Use kwargs so can return a default value of None"""
    if a not in el.attrib:
        if "d" in kwargs:
            return kwargs["d"]
        raise ValueError(f"Was expecting element '{el.tag}' to have attribute '{a}', but it does not")
    return f(el.attrib[a])


def iattrib(el, a, d=None, r=None) -> int:
    v = attrib(el, a, f=int, d=d)
    if r:
        if v not in r:
            raise ValueError(f"Value for '{a}' in '{el.tag}' needs to lie in range {r.start} to {r.stop}, not '{v}'")
    return v


def fattrib(el, a, d=None, r=None) -> float:
    v = attrib(el, a, f=float, d=d)
    if r:
        if v not in r:
            raise ValueError(f"Value for '{a}' in '{el.tag}' needs to lie in range {r.start} to {r.stop}, not '{v}'")
    return v


def battrib(el, a, d) -> bool:
    return attrib(el, a, f=lambda s: s.lower() in ["true", "yes", "1"], d=d)


def rgbattr(el, a, d) -> Optional[Tuple]:
    v = attrib(el, a, f=lambda s: tuple(map(int, s.split(","))), d=d)
    if v is None:
        return v
    if len(v) != 3 and len(v) != 4:
        raise ValueError(
            f"RGB value for '{a}' in '{el.tag}' needs to be 3 numbers (r,g,b), or 4 (r,g,b,a) not {len(v)}"
        )
    return v


def at(el) -> Coordinate:
    return Coordinate(iattrib(el, "x", d=0), iattrib(el, "y", d=0))


def metric_accessor_from(name: str) -> Callable[[Entry], Optional[pint.Quantity]]:
    accessors = {
        "hr": lambda e: e.hr,
        "cadence": lambda e: e.cad,
        "power": lambda e: e.power,
        "speed": lambda e: e.speed if e.speed is not None else e.cspeed,
        "cspeed": lambda e: e.cspeed,
        "accel": lambda e: e.accel,
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
        "sdps": lambda e: e.sdps, # Vaaka cadence sensor distance-per-stroke field
    }
    if name in accessors:
        return accessors[name]
    elif name.startswith("custom.field.") or name.startswith("custom.metadata.") or name.startswith("custom.ref."):
        def f(e):
            try:
                metric = e.custom[name.split(".")[1]][name.split(".", 2)[2]]
                return units.Quantity(metric, units.custom) if metric else None
            except KeyError:
                return None # Custom field not found
        return f
    raise IOError(f"The metric '{name}' is not supported. Use one of: {list(accessors.keys()) + ['custom.field', 'custom.metadata', 'custom.ref']}")


def quantity_formatter_for(format_string: Optional[str], dp: Optional[int]) -> Callable[[pint.Quantity], str]:
    if format_string and dp:
        raise IOError("Cannot supply both 'format' and 'dp', just use one")

    if format_string is None and dp is None:
        dp = 2

    if format_string is not None:
        def f(q):
            if type(q.m) == str:
                raise ValueError("String values cannot be formatted")
            if format_string == "pace":
                # pace is in minutes, and we want minutes / seconds
                return '{:d}:{:02d}'.format(*divmod(math.ceil(60.0 * q.m), 60))
            try:
                return format(q.m, format_string)
            except ValueError:
                raise ValueError(f"Unable to format value with format string {format_string}")
        return f
    elif dp is not None:
        # hack to allow for custom fields or metadata to be passed through
        def f(q):
            if type(q.m) == str:
                return q.m
            return format(q.m, f".{dp}f")
        return f
    else:
        raise Defect("Problem deciding how to format")


def quantity_formatter_from(element) -> Callable[[pint.Quantity], str]:
    return quantity_formatter_for(
        attrib(element, "format", d=None),
        iattrib(element, "dp", d=None)
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


@dataclasses.dataclass(frozen=True)
class FloatRange:
    start: float
    stop: float

    def __contains__(self, item):
        if type(item) != float:
            return NotImplemented
        return self.start <= item <= self.stop


class Widgets:

    def __init__(self, font, privacy, renderer, framemeta, converters, xml_path=None):
        self.framemeta = framemeta
        self.renderer = renderer
        self.privacy = privacy
        self.font = font
        self.converters = converters
        self.xml_path = xml_path

    def _font(self, element, name, d):
        return self.font(iattrib(element, name, d=d, r=range(1, 2000)))

    @allow_attributes(
        {"x", "y", "metric", "size", "format", "dp", "units", "align", "cache", "rgb", "outline", "outline_width"})
    def create_metric(self, element, entry, **kwargs) -> Widget:
        return metric(
            at=at(element),
            entry=entry,
            accessor=metric_accessor_from(attrib(element, "metric")),
            formatter=quantity_formatter_from(element),
            font=self._font(element, "size", d=16),
            converter=self.converters.converter(attrib(element, "units", d=None)),
            align=attrib(element, "align", d="left"),
            cache=battrib(element, "cache", d=True),
            fill=rgbattr(element, "rgb", d=(255, 255, 255)),
            stroke=rgbattr(element, "outline", d=(0, 0, 0)),
            stroke_width=iattrib(element, "outline_width", d=2),
        )

    @allow_attributes({"x", "y", "metric", "size", "units", "align", "rgb", "outline", "outline_width"})
    def create_metric_unit(self, element: ET.Element, entry, **kwargs) -> Widget:

        format_string = element.text or "{:~C}"

        return metric(
            at=at(element),
            entry=entry,
            accessor=metric_accessor_from(attrib(element, "metric")),
            formatter=lambda q: format_string.format(q.u),
            font=self._font(element, "size", d=16),
            converter=self.converters.converter(attrib(element, "units", d=None)),
            align=attrib(element, "align", d="left"),
            cache=True,
            fill=rgbattr(element, "rgb", d=(255, 255, 255)),
            stroke=rgbattr(element, "outline", d=(0, 0, 0)),
            stroke_width=iattrib(element, "outline_width", d=2),
        )

    @allow_attributes({"x", "y", "file", "size", "invert"})
    def create_icon(self, element, **kwargs) -> Widget:
        return simple_icon(
            at=at(element),
            file=attrib(element, "file"),
            size=iattrib(element, "size", d=64),
            invert=battrib(element, "invert", d=True),
            xml_path=self.xml_path
        )

    @allow_attributes({"x", "y", "size", "format", "truncate", "align", "cache", "rgb", "outline", "outline_width"})
    def create_datetime(self, element, entry, **kwargs):
        return text(
            at=at(element),
            value=date_formatter_from_element(element, entry),
            font=self._font(element, "size", d=16),
            align=attrib(element, "align", d="left"),
            cache=battrib(element, "cache", d=True),
            fill=rgbattr(element, "rgb", d=(255, 255, 255)),
            stroke=rgbattr(element, "outline", d=(0, 0, 0)),
            stroke_width=iattrib(element, "outline_width", d=2)
        )

    @allow_attributes({"x", "y", "size", "align", "direction", "rgb", "outline", "outline_width"})
    def create_text(self, element: ET.Element, entry, **kwargs) -> Widget:
        if element.text is None:
            raise IOError("Text components should have the text in the element like <component...>Text</component>")

        return text(
            at=at(element),
            value=lambda: element.text,
            font=self._font(element, "size", d=16),
            align=attrib(element, "align", d="left"),
            direction=attrib(element, "direction", d="ltr"),
            fill=rgbattr(element, "rgb", d=(255, 255, 255)),
            stroke=rgbattr(element, "outline", d=(0, 0, 0)),
            stroke_width=iattrib(element, "outline_width", d=2),
        )

    @allow_attributes({"x", "y", "size", "zoom", "corner_radius", "opacity", "rotate", "map_style"})
    def create_moving_map(self, element: ET.Element, entry, **kwargs) -> Widget:
        return moving_map(
            at=at(element),
            entry=entry,
            size=iattrib(element, "size", d=256),
            zoom=iattrib(element, "zoom", d=16, r=range(1, 20)),
            renderer=self.renderer,
            corner_radius=iattrib(element, "corner_radius", 0),
            opacity=fattrib(element, "opacity", 0.7, r=FloatRange(0.0, 1.0)),
            rotate=battrib(element, "rotate", d=True),
            map_style=attrib(element, "map_style", d="")
        )

    @allow_attributes({"x", "y", "size", "corner_radius", "opacity", "map_style", "pos_rgb", "pos_size", "path_rgb", "path_width", "wpt_rgb", "wpt_size"})
    def create_journey_map(self, element: ET.Element, entry, **kwargs) -> Widget:
        return journey_map(
            at(element),
            entry,
            privacy_zone=self.privacy,
            renderer=self.renderer,
            timeseries=self.framemeta,
            size=iattrib(element, "size", d=256),
            corner_radius=iattrib(element, "corner_radius", 0),
            opacity=fattrib(element, "opacity", 0.7, r=FloatRange(0.0, 1.0)),
            map_style=attrib(element, "map_style", d=""),
            style={
                "pos_rgb": rgbattr(element, "pos_rgb", d=(0, 0, 255)),
                "pos_size": iattrib(element, "pos_size", d=6),
                "path_rgb": rgbattr(element, "path_rgb", d=(255, 0, 0)),
                "path_width": iattrib(element, "path_width", d=4),
                "wpt_rgb": rgbattr(element, "wpt_rgb", d=(0, 255, 0)),
                "wpt_size": iattrib(element, "wpt_size", d=6)
            }
        )

    @allow_attributes({"size", "zoom", "map_style", "pos_rgb", "pos_size", "path_rgb", "path_width", "wpt_rgb", "wpt_size"})
    def create_moving_journey_map(self, element: ET.Element, entry, **kwargs) -> Widget:
        return MovingJourneyMap(
            location=lambda: entry().point,
            waypoints=lambda: entry().custom["waypoints"],
            privacy_zone=self.privacy,
            renderer=self.renderer,
            timeseries=self.framemeta,
            size=iattrib(element, "size", d=256),
            zoom=iattrib(element, "zoom", d=16, r=range(1, 20)),
            map_style=attrib(element, "map_style", d=""),
            style={
                "pos_rgb": rgbattr(element, "pos_rgb", d=(0, 0, 255)),
                "pos_size": iattrib(element, "pos_size", d=6),
                "path_rgb": rgbattr(element, "path_rgb", d=(255, 0, 0)),
                "path_width": iattrib(element, "path_width", d=4),
                "wpt_rgb": rgbattr(element, "wpt_rgb", d=(0, 255, 0)),
                "wpt_size": iattrib(element, "wpt_size", d=6)
            }
        )

    @allow_attributes({"size", "fill", "outline", "fill_width", "outline_width"})
    def create_circuit_map(self, element: ET.Element, entry, **kwargs) -> Widget:
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

    @allow_attributes({"x", "y", "metric", "units", "seconds",
                       "samples", "values", "textsize", "filled",
                       "height", "bg", "fill", "line", "text"})
    def create_chart(self, element: ET.Element, entry, **kwargs) -> Widget:
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

        title = self._font(element, "textsize", d=16)
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
                fill=rgbattr(element, "fill", d=(91, 113, 146, 170)),
                line=rgbattr(element, "line", d=(255, 255, 255, 170)),
                text=rgbattr(element, "text", d=(255, 255, 255, 170)),
            )
        )

    @allow_attributes({"size", "textsize", "fg", "bg", "text"})
    def create_compass(self, element: ET.Element, entry, **kwargs) -> Widget:
        return Compass(
            size=iattrib(element, "size", d=256),
            reading=lambda: nonesafe(entry().cog),
            font=self._font(element, "textsize", d=16),
            fg=rgbattr(element, "fg", d=(255, 255, 255)),
            bg=rgbattr(element, "bg", d=None),
            text=rgbattr(element, "text", d=(255, 255, 255)),
        )

    @allow_attributes({"size", "textsize", "arrow", "bg", "text", "outline", "arrow-outline"})
    def create_compass_arrow(self, element: ET.Element, entry, **kwargs) -> Widget:
        return CompassArrow(
            size=iattrib(element, "size", d=256),
            reading=lambda: nonesafe(entry().cog),
            font=self.font(iattrib(element, "textsize", d=32)),
            arrow=rgbattr(element, "arrow", d=(255, 255, 255)),
            bg=rgbattr(element, "bg", d=(0, 0, 0, 0)),
            text=rgbattr(element, "text", d=(255, 255, 255)),
            outline=rgbattr(element, "outline", d=(0, 0, 0)),
            arrow_outline=rgbattr(element, "arrow-outline", d=(0, 0, 0)),
        )

    @allow_attributes({"width", "height", "metric", "units", "fill", "zero", "bar", "align_center",
                       "outline", "outline-width", "h-neg", "h-pos", "max", "min", "cr"})
    def create_bar(self, element: ET.Element, entry, **kwargs) -> Widget:
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
            align_center=battrib(element, "align_center", d=False),
            outline=rgbattr(element, "outline", d=(255, 255, 255)),
            outline_width=iattrib(element, "outline-width", d=3),
            highlight_colour_negative=rgbattr(element, "h-neg", d=(255, 0, 0)),
            highlight_colour_positive=rgbattr(element, "h-pos", d=(0, 255, 0)),
            max_value=iattrib(element, "max", d=20),
            min_value=iattrib(element, "min", d=-20),
            cr=iattrib(element, "cr", d=5),
        )

    @allow_attributes({"width", "height", "metric", "units", "fill", "zone-divider", "outline",
                       "outline-width", "cr", "max", "min", "z1", "z2", "z3", "z0-rgb", "z1-rgb",
                       "z2-rgb", "z3-rgb"})
    def create_zone_bar(self, element: ET.Element, entry, **kwargs):
        return GradientBar(
            size=Dimension(
                x=iattrib(element, "width", d=400),
                y=iattrib(element, "height", d=30)
            ),
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
            max_value=iattrib(element, "max", d=400),
            min_value=iattrib(element, "min", d=0),
            z1_value=iattrib(element, "z1", d=120),
            z2_value=iattrib(element, "z2", d=160),
            z3_value=iattrib(element, "z3", d=200),
            z0_col=rgbattr(element, "z0-rgb", d=(255, 255, 255)),
            z1_col=rgbattr(element, "z1-rgb", d=(67, 235, 52)),
            z2_col=rgbattr(element, "z2-rgb", d=(240, 232, 19)),
            z3_col=rgbattr(element, "z3-rgb", d=(207, 19, 2)),
        )

    @allow_attributes({"size", "metric", "units", "textsize", "vs0", "vs", "vfe", "vno", "vne", "rotate"})
    def create_asi(self, element: ET.Element, entry, **kwargs) -> Widget:
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

    @allow_attributes({"size", "metric", "units", "textsize", "needle", "green", "yellow", "end", "rotate", "outline"})
    def create_msi(self, element: ET.Element, entry, **kwargs) -> Widget:
        return MotorspeedIndicator(
            size=iattrib(element, "size", d=256),
            reading=metric_value(
                entry,
                accessor=metric_accessor_from(attrib(element, "metric", d="speed")),
                converter=self.converters.converter(attrib(element, "units", d="knots")),
                formatter=lambda q: q.m,
                default=0
            ),
            font=self.font(iattrib(element, "textsize", d=16)),
            needle=battrib(element, "needle", d=True),
            green=iattrib(element, "green", d=0),
            yellow=iattrib(element, "yellow", d=130),
            end=iattrib(element, "end", d=180),
            rotate=iattrib(element, "rotate", d=180),
            outline=iattrib(element, "outline", d=2)
        )

    @allow_attributes({"size", "metric", "units", "textsize", "green", "yellow", "end", "rotate", "outline"})
    def create_msi2(self, element: ET.Element, entry, **kwargs) -> Widget:
        return MotorspeedIndicator2(
            size=iattrib(element, "size", d=256),
            reading=metric_value(
                entry,
                accessor=metric_accessor_from(attrib(element, "metric", d="speed")),
                converter=self.converters.converter(attrib(element, "units", d="knots")),
                formatter=lambda q: q.m,
                default=0
            ),
            font=self.font(iattrib(element, "textsize", d=16)),
            green=iattrib(element, "green", d=0),
            yellow=iattrib(element, "yellow", d=130),
            end=iattrib(element, "end", d=180),
            rotate=iattrib(element, "rotate", d=180),
            outline=iattrib(element, "outline", d=2)
        )

    @allow_attributes({"size", "lock_none", "lock_unknown", "lock_2d", "lock_3d"})
    def create_gps_lock_icon(self, element: ET.Element, entry, **kwargs) -> Widget:
        at = Coordinate(0, 0)
        size = iattrib(element, "size", d=64)
        return GPSLock(
            fix=lambda: entry().gpsfix,
            lock_no=simple_icon(at, attrib(element, "lock_none", d="gps_lock_none.png"), size),
            lock_unknown=simple_icon(at, attrib(element, "lock_unknown", d="gps_lock_unknown.png"), size),
            lock_2d=simple_icon(at, attrib(element, "lock_2d", d="gps_lock_2d.png"), size),
            lock_3d=simple_icon(at, attrib(element, "lock_3d", d="gps_lock_3d.png"), size),
        )

    def with_cairo(self, f: Callable):
        try:
            import gopro_overlay.layout_xml_cairo
            return f(gopro_overlay.layout_xml_cairo)
        except ModuleNotFoundError:
            raise IOError("This widget needs pycairo to be installed - please see docs") from None

    def create_cairo_circuit_map(self, element: ET.Element, entry, **kwargs):
        return self.with_cairo(lambda m: m.create_cairo_circuit_map(element, entry, self.framemeta, **kwargs))

    def create_cairo_gauge_marker(self, element: ET.Element, entry, **kwargs):
        return self.with_cairo(lambda m: m.create_cairo_gauge_marker(element, entry, self.converters, **kwargs))

    def create_cairo_gauge_round_annotated(self, element: ET.Element, entry, **kwargs):
        return self.with_cairo(
            lambda m: m.create_cairo_gauge_round_annotated(element, entry, self.converters, **kwargs))

    def create_cairo_gauge_arc_annotated(self, element: ET.Element, entry, **kwargs):
        return self.with_cairo(lambda m: m.create_cairo_gauge_arc_annotated(element, entry, self.converters, **kwargs))

    def create_cairo_gauge_donut(self, element, entry: ET.Element, **kwargs):
        return self.with_cairo(lambda m: m.create_cairo_gauge_donut(element, entry, self.converters, **kwargs))
