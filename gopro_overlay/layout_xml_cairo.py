from .dimensions import Dimension
from .layout_xml import iattrib, rgbattr, fattrib
from .widgets.cairo.cairo import CairoWidget
from .widgets.cairo.circuit import CairoCircuit
from .widgets.cairo.circuit import Line
from .widgets.widgets import Widget


def create_cairo_circuit_map(element, entry, privacy, renderer, timeseries, **kwargs) -> Widget:
    size = iattrib(element, "size", d=256)
    rotation = iattrib(element, "rotate", d=0)

    return CairoWidget(
        size=Dimension(size, size),
        rotation=rotation,
        widgets=[
            CairoCircuit(
                framemeta=timeseries,
                location=lambda: entry().point,
                line=Line(
                    fill=rgbattr(element, "fill", d=(255, 255, 255)),
                    outline=rgbattr(element, "outline", d=(255, 0, 0)),
                    width=fattrib(element, "line_width", d=0.01),
                ),
                loc=Line(
                    fill=rgbattr(element, "loc_fill", d=(0, 0, 255)),
                    outline=rgbattr(element, "loc_outline", d=(0, 0, 0)),
                    width=fattrib(element, "loc_size", d=0.01 * 1.1)
                )
            )
        ]
    )
