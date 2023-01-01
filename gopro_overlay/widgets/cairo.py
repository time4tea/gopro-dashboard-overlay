import contextlib

import cairo
from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.exceptions import Defect


@contextlib.contextmanager
def saved(context: cairo.Context):
    context.save()
    try:
        yield
    finally:
        context.restore()


def to_pillow(surface: cairo.ImageSurface) -> Image:
    size = (surface.get_width(), surface.get_height())
    stride = surface.get_stride()

    format = surface.get_format()
    if format != cairo.FORMAT_ARGB32:
        raise Defect(f"Only support ARGB32 images, not {format}")

    with surface.get_data() as memory:
        return Image.frombuffer("RGBA", size, memory.tobytes(), 'raw', "BGRa", stride)


class CairoWidget:

    def __init__(self, size: Dimension, widgets):
        self.size = size
        self.widgets = widgets

    def draw(self, image: Image, draw: ImageDraw):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size.x, self.size.y)
        ctx = cairo.Context(surface)
        ctx.scale(surface.get_width(), surface.get_height())

        for widget in self.widgets:
            widget.draw(ctx)

        image.alpha_composite(to_pillow(surface), (0, 0))
