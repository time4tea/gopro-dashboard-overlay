import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.bordered import AbstractBordered, cos45
from gopro_overlay.widgets.cairo.box import abox
from gopro_overlay.widgets.cairo.colour import Colour, BLACK


class Cap(AbstractBordered):
    def __init__(self, centre: Coordinate, radius: float, cfrom: Colour, cto: Colour):
        super().__init__()
        self.centre = centre
        self.radius = radius
        self.cfrom = cfrom
        self.cto = cto

        self.pattern: cairo.LinearGradient = None
        self.mask: cairo.RadialGradient = None

    def init(self):
        pattern = cairo.LinearGradient(-cos45, -cos45, cos45, cos45)
        pattern.add_color_stop_rgba(0.0, *self.cfrom.rgba())
        pattern.add_color_stop_rgba(1.0, *self.cto.rgba())

        mask = cairo.RadialGradient(
            0.0, 0.0, 0.0,
            0.0, 0.0, 1.0
        )
        mask.add_color_stop_rgba(0.0, *BLACK.rgba())
        mask.add_color_stop_rgba(1.0, *BLACK.rgba())
        mask.add_color_stop_rgba(1.00001, *BLACK.alpha(0).rgba())

        self.pattern = pattern
        self.mask = mask

    # def draw(self, context: cairo.Context):
    #     with saved(context):
    #         context.new_path()
    #         context.set_line_width(0.01)
    # self.set_contents_path(context)
    # context.close_path()
    # self.draw_contents(context)

    def set_contents_path(self, context: cairo.Context):
        context.arc(self.centre.x, self.centre.y, self.radius, 0.0, math.tau)

    def draw_contents(self, context: cairo.Context):
        if self.pattern is None:
            self.init()

        box = abox(*context.path_extents())
        print(box)
        r = 0.5 * (box.x2 - box.x1)

        matrix = context.get_matrix()
        matrix.xx = r
        matrix.x0 = matrix.x0 + 0.5 * (box.x1 + box.x2)
        matrix.yy = r
        matrix.y0 = matrix.y0 + 0.5 + (box.y1 + box.y2)

        context.set_matrix(matrix)
        context.set_source(self.pattern)
        context.mask(self.mask)
        # context.stroke()



