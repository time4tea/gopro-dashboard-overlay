import cairo

from gopro_overlay.widgets.cairo.bordered import AbstractBordered, Border
from gopro_overlay.widgets.cairo.colour import Colour, BLACK
from gopro_overlay.widgets.cairo.ellipse import Arc


class CairoEllipticBackground(AbstractBordered):
    def __init__(self, arc: Arc, colour: Colour = BLACK, border=Border.NONE()):
        super().__init__(border=border)
        self.arc = arc
        self.colour = colour

    def set_contents_path(self, context: cairo.Context):
        self.arc.draw(context)

    def draw_contents(self, context: cairo.Context):
        context.set_source_rgba(*self.colour.rgba())
        context.fill()
