import dataclasses
import math
from enum import Enum, auto

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.box import abox
from gopro_overlay.widgets.cairo.cairo import saved, CairoWidget
from gopro_overlay.widgets.cairo.colour import Colour, BLACK


class DrawingAction(Enum):
    Region = auto()
    Line = auto()
    Contents = auto()


class ShadowMode(Enum):
    ShadowNone = auto()
    ShadowIn = auto()
    ShadowOut = auto()
    ShadowEtchedIn = auto()
    ShadowEtchedOut = auto()


@dataclasses.dataclass
class Border:
    width: float
    depth: float
    shadow: ShadowMode
    colour: Colour

    @staticmethod
    def NONE() -> 'Border':
        return Border(width=0.0, depth=0.0, shadow=ShadowMode.ShadowNone, colour=BLACK)


cos45 = math.sqrt(2.0) * 0.5
darkenBy = 1.0 / 3
lightenBy = 1.0 / 3


class AbstractBordered(CairoWidget):
    def __init__(self, border: Border = Border.NONE()):
        self.border_width = border.width
        self.border_depth = border.depth
        self.border_shadow = border.shadow
        self.border_colour = border.colour

    def set_contents_path(self, context: cairo.Context):
        pass

    def draw_contents(self, context: cairo.Context):
        pass

    def draw(self, context: cairo.Context):

        if self.border_width > 0:
            shadow_depth = self.border_depth
        else:
            shadow_depth = 0.0

        with saved(context):
            context.new_path()
            self.set_contents_path(context)
            context.close_path()

            box = abox(*context.path_extents())

            extent = abs(box.x2 - box.x1)

            print(box)

            box_centre = Coordinate(
                x=(box.x2 + box.x1) * 0.5,
                y=(box.y2 + box.y1) * 0.5
            )

            def _draw(shift: float, bound: float, width: float, action: DrawingAction = DrawingAction.Line):
                F = (bound - width) / extent
                S = shift * shadow_depth * 0.5

                FX = F
                FY = F

                context.new_path()
                context.scale(FX, FY)
                context.translate(
                    box_centre.x * (1.0 / FX - 1.0) + S * cos45 / FX,
                    box_centre.y * (1.0 / FY - 1.0) + S * cos45 / FY
                )
                context.append_path(path)
                context.set_line_width(width / F)

                if action == DrawingAction.Line:
                    context.stroke()
                elif action == DrawingAction.Region:
                    context.fill()
                elif action == DrawingAction.Contents:
                    self.draw_contents(context)

            outer_size = extent
            inner_size = extent - 2.0 * self.border_width

            if self.border_shadow == ShadowMode.ShadowNone:
                middle_size = outer_size
            elif self.border_shadow == ShadowMode.ShadowIn:
                inner_size = inner_size - 2.0 * shadow_depth
                middle_size = outer_size
            elif self.border_shadow == ShadowMode.ShadowOut:
                inner_size = inner_size - shadow_depth
                middle_size = outer_size - 2.0 * shadow_depth
            elif self.border_shadow in [ShadowMode.ShadowEtchedIn, ShadowMode.ShadowEtchedOut]:
                inner_size = inner_size - 4.0 * shadow_depth
                middle_size = outer_size - 2.0 * shadow_depth

            def set_normal():
                context.set_source_rgba(*self.border_colour.rgba())

            def set_light():
                context.set_source_rgba(*self.border_colour.lighten(lightenBy).rgba())

            def set_dark():
                context.set_source_rgba(*self.border_colour.darken(darkenBy).rgba())

            if inner_size > 0:
                path = context.copy_path()

                if self.border_shadow == ShadowMode.ShadowNone:
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                elif self.border_shadow == ShadowMode.ShadowIn:
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                    set_dark()
                    _draw(-1.0, inner_size + shadow_depth, shadow_depth)
                    set_light()
                    _draw(1.0, inner_size + shadow_depth, shadow_depth)
                elif self.border_shadow == ShadowMode.ShadowOut:
                    set_light()
                    _draw(-1.0, outer_size - shadow_depth, shadow_depth)
                    set_dark()
                    _draw(1.0, outer_size - shadow_depth, shadow_depth)
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                elif self.border_shadow == ShadowMode.ShadowEtchedIn:
                    set_dark()
                    _draw(-1.0, outer_size - shadow_depth, shadow_depth)
                    set_light()
                    _draw(1.0, outer_size - shadow_depth, shadow_depth)
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                    set_light()
                    _draw(-1.0, inner_size + shadow_depth, shadow_depth)
                    set_dark()
                    _draw(1.0, inner_size + shadow_depth, shadow_depth)
                elif self.border_shadow == ShadowMode.ShadowEtchedOut:
                    set_light()
                    _draw(-1.0, outer_size - shadow_depth, shadow_depth)
                    set_dark()
                    _draw(1.0, outer_size - shadow_depth, shadow_depth)
                    if self.border_width > 0.0:
                        set_normal()
                        _draw(0.0, middle_size, 0.0)
                    set_dark()
                    _draw(-1.0, inner_size + shadow_depth, shadow_depth)
                    set_light()
                    _draw(1.0, inner_size + shadow_depth, shadow_depth)
                _draw(0.0, inner_size, 0.0, DrawingAction.Contents)
