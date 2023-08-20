import dataclasses
import math
from typing import Callable

import cairo

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.cairo import saved, CairoWidget
from gopro_overlay.widgets.cairo.reading import Reading
from gopro_overlay.widgets.cairo.colour import Colour


@dataclasses.dataclass(frozen=True)
class NeedleParameter:
    width: float
    length: float
    cap: cairo.LineCap = cairo.LINE_CAP_BUTT

    @property
    def radius(self):
        return self.width / 2.0


class Needle(CairoWidget):

    def __init__(self, centre: Coordinate,
                 reading: Callable[[], Reading],
                 start: Angle,
                 length: Angle,
                 tip: NeedleParameter,
                 rear: NeedleParameter,
                 colour: Colour):
        self.centre = centre
        self.colour = colour
        self.rear = rear
        self.tip = tip
        self.length = length
        self.start = start
        self.reading = reading

    def draw(self, context: cairo.Context):
        with saved(context):
            context.new_path()
            context.translate(*self.centre.tuple())
            context.rotate((self.start + self.reading().value() * self.length).radians())

            tip = self.tip
            rear = self.rear

            if tip.cap == cairo.LINE_CAP_BUTT:
                context.move_to(tip.length, -tip.radius)
                context.line_to(tip.length, tip.radius)
            elif tip.cap == cairo.LINE_CAP_ROUND:

                angle = math.atan2(
                    tip.radius - rear.radius,
                    tip.length + rear.length
                )
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                context.move_to(tip.length + tip.radius * sin_angle, -tip.radius * cos_angle)
                context.arc(tip.length, 0.0, tip.radius, angle - math.pi / 2.0, math.pi / 2.0 - angle)
                context.line_to(tip.length + tip.radius * sin_angle, tip.radius * cos_angle)

            elif tip.cap == cairo.LINE_CAP_SQUARE:
                context.move_to(tip.length, -tip.radius)
                context.line_to(tip.length + tip.radius * math.sqrt(2.0), 0.0)
                context.line_to(tip.length, tip.radius)
            else:
                raise ValueError("Unsupported needle tip type")

            if rear.cap == cairo.LINE_CAP_BUTT:
                context.line_to(-rear.length, rear.radius)
                context.line_to(-rear.length, -rear.radius)
            elif rear.cap == cairo.LINE_CAP_ROUND:
                angle = math.atan2(
                    rear.radius - tip.radius,
                    tip.length + rear.length
                )
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                context.line_to(-rear.length - rear.radius * sin_angle, rear.radius * cos_angle)
                context.arc(-rear.length, 0.0, rear.radius, math.pi / 2.0 - angle, angle - math.pi / 2.0)
                context.line_to(-rear.length - rear.radius * sin_angle, -rear.radius * cos_angle)

            elif rear.cap == cairo.LINE_CAP_SQUARE:
                context.line_to(-rear.length, rear.radius)
                context.line_to(-rear.length - rear.radius * math.sqrt(2.0), 0.0)
                context.line_to(-rear.length, -rear.radius)
            else:
                raise ValueError("Unsupported needle rear type")

            context.close_path()
            context.set_source_rgba(*self.colour.rgba())

            context.fill()
