from .dimensions import Dimension
from .layout_xml import iattrib, rgbattr, fattrib
from .layout_xml_attribute import allow_attributes
from .widgets.cairo.cairo import CairoAdapter
from .widgets.cairo.circuit import CairoCircuit
from .widgets.cairo.circuit import Line
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
