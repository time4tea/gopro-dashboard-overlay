import contextlib
import math
from typing import Tuple, List, Optional

import cairo
from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.exceptions import Defect
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.widgets import Widget


class CairoWidget:
    def draw(self, context: cairo.Context):
        raise NotImplemented()


class NullCairoWidget(CairoWidget):
    def draw(self, context: cairo.Context):
        pass


class CairoTranslate(CairoWidget):
    def __init__(self, by: Coordinate, widget: CairoWidget):
        self.by = by
        self.widget = widget

    def draw(self, context: cairo.Context):
        with saved(context):
            context.translate(*self.by.tuple())
            self.widget.draw(context)


class CairoComposite(CairoWidget):
    def __init__(self, widgets: List[CairoWidget]):
        self.widgets = widgets

    def draw(self, context: cairo.Context):
        for w in self.widgets:
            w.draw(context)


class CairoCache(CairoWidget):
    def __init__(self, widget: CairoWidget):
        self.surface: Optional[cairo.Surface] = None
        self.widget = widget

    def copy(self, context: cairo.Context):
        target: cairo.ImageSurface = context.get_target()
        surface = target.create_similar(cairo.Content.COLOR_ALPHA, target.get_width(), target.get_height())
        cachecontext = cairo.Context(surface)
        cachecontext.set_operator(cairo.OPERATOR_SOURCE)
        cachecontext.set_source_surface(target)
        cachecontext.paint()
        return surface

    def draw(self, context: cairo.Context):
        if self.surface is None:
            self.widget.draw(context)
            self.surface = self.copy(context)
        else:
            new_context = cairo.Context(context.get_target())
            new_context.set_operator(cairo.OPERATOR_SOURCE)
            new_context.set_source_surface(self.surface)
            new_context.paint()


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


class CairoAdapter(Widget):

    def __init__(self, size: Dimension, widget: CairoWidget, rotation=0):
        self.size = size
        self.rotation = rotation
        self.widget = widget

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

        self.widget.draw(ctx)

        image.alpha_composite(to_pillow(surface), (0, 0))


def set_source(context: cairo.Context, colour: Tuple):
    n = len(colour)
    if n == 3:
        context.set_source_rgb(*colour)
    elif n == 4:
        context.set_source_rgba(*colour)
    else:
        raise ValueError(f"Colour tuple is {n}: expected 3 or 4")
