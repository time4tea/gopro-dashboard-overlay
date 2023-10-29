import math
from enum import Enum, auto
from typing import List

import cairo

from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.cairo import saved
from gopro_overlay.widgets.cairo.colour import Colour
from gopro_overlay.widgets.cairo.ellipse import EllipseParameters
from gopro_overlay.widgets.cairo.face import FontFace
from gopro_overlay.widgets.cairo.tick import TickParameters


class AnnotationMode(Enum):
    MovedInside = auto()
    MovedOutside = auto()
    MovedCentred = auto()
    Rotated = auto()
    Skewed = auto()


class EllipticAnnotation:

    def __init__(self,
                 ellipse: EllipseParameters,
                 tick: TickParameters,
                 colour: Colour,
                 face: FontFace,
                 mode: AnnotationMode,
                 texts: List[str],
                 height: float,
                 stretch: float,
                 start: Angle,
                 length: Angle):
        self.mode = mode
        self.texts = texts
        self.face = face
        self.colour = colour
        self.tick = tick
        self.ellipse = ellipse
        self.start = start
        self.original_length = length
        self.length = length + tick.step * 0.05
        self.height = height
        self.stretch = stretch

    def draw(self, context: cairo.Context):

        context.set_source_rgba(*self.colour.rgba())
        thick = self.tick.first

        for i in range(0, 1_000_000):
            angle = self.tick.step * i
            if angle > self.length:
                break
            if self.original_length < Angle.zero():
                angle = -angle
            if thick == self.tick.skipped:
                thick = 1
            else:
                thick += 1

            angle_r = (self.start + angle).radians()

            point = self.ellipse.get_point(self.ellipse * angle_r)

            if i >= len(self.texts):
                break

            text = self.texts[i]
            extents = self.face.text_extents(context, text)

            with saved(context):
                if extents.height > 0.0:
                    gain = self.height / extents.height

                    context.translate(*point.tuple())

                    if self.mode == AnnotationMode.MovedInside:
                        context.translate(
                            (-extents.width * 0.5 * gain * self.stretch * math.cos(angle_r)),
                            (-extents.height * 0.5 * gain * math.sin(angle_r))
                        )
                    elif self.mode == AnnotationMode.MovedOutside:
                        raise NotImplementedError("Moved Outside")
                    elif self.mode == AnnotationMode.MovedCentred:
                        # nothing to do
                        pass
                    elif self.mode == AnnotationMode.Rotated:
                        raise NotImplementedError("Rotated")
                    elif self.mode == AnnotationMode.Skewed:
                        raise NotImplementedError("Skewed")

                    context.scale(gain * self.stretch, gain)
                    context.move_to(
                        -(extents.x_bearing + extents.width * 0.5),
                        -(extents.y_bearing + extents.height * 0.5)
                    )

                    self.face.show(context, text)


def create_texts(v_min, v_max, sectors):
    v_range = v_max - v_min
    each = v_range / sectors

    current = v_min
    values = []
    while current <= v_max:
        values.append(f"{int(current)}")
        current += each

    return values


def distribute(l, n):
    return [l[i::n] for i in range(n)]
