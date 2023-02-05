import dataclasses

import cairo

from gopro_overlay.widgets.cairo.colour import Colour


@dataclasses.dataclass(frozen=True)
class LineParameters:
    width: float
    colour: Colour = Colour(1.0, 1.0, 1.0)
    cap: cairo.LineCap = cairo.LINE_CAP_SQUARE

    def apply_to(self, context: cairo.Context):
        self.colour.apply_to(context)
        context.set_line_cap(self.cap)
        context.set_line_width(self.width)
