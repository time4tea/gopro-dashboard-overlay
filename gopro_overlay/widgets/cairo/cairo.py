import contextlib
import math
from typing import Tuple

import cairo
from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.exceptions import Defect


class CairoCache:
    def __init__(self):
        self.surface = None

    def store(self, context: cairo.Context):
        target: cairo.ImageSurface = context.get_target()
        self.surface = cairo.Surface.create_similar(
            content=target,
            width=target.get_width(),
            height=target.get_height()
        )

    def draw(self, context: cairo.Context):
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.set_source_surface(self.surface)
        context.paint()


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

    def __init__(self, size: Dimension, rotation=0, widgets=None):
        self.size = size
        self.rotation = rotation
        self.widgets = [] if widgets is None else widgets

    def draw(self, image: Image, draw: ImageDraw):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size.x, self.size.y)
        ctx = cairo.Context(surface)
        ctx.scale(surface.get_width(), surface.get_height())
        ctx.translate(0.5, 0.5)

        if self.rotation != 0:
            # Need to scale to stop points being clipped outside image
            # consider point at (1,1)
            ctx.rotate(math.radians(self.rotation))
            rotate = math.radians(self.rotation)
            scale = max(math.cos(rotate) + math.sin(rotate), math.cos(rotate) - math.sin(rotate))
            if scale > 1.0:
                ctx.scale(1 / scale, 1 / scale)

        for widget in self.widgets:
            widget.draw(ctx)

        image.alpha_composite(to_pillow(surface), (0, 0))


def set_source(context: cairo.Context, colour: Tuple):
    n = len(colour)
    if n == 3:
        context.set_source_rgb(*colour)
    elif n == 4:
        context.set_source_rgba(*colour)
    else:
        raise ValueError(f"Colour tuple is {n}: expected 3 or 4")
