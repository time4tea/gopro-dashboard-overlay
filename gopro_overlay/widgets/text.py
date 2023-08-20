from typing import Callable, Any, Tuple

from PIL import Image, ImageDraw

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.widgets import Widget


class CachingText(Widget):
    def __init__(self, at: Coordinate, value: Callable, font,
                 align="left", direction="ltr",
                 fill=None,
                 stroke=(0, 0, 0),
                 stroke_width=2,
                 ):
        self.at = at
        self.value = value
        self.font = font
        self.anchor = anchors.get(align, align)
        self.direction = direction
        self.fill = fill if fill else (255, 255, 255)
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.cache = {}

    def draw(self, image: Image, draw: ImageDraw):

        text = self.value()

        if text is None:
            raise ValueError("Refusing to draw text with value of 'None'")

        cached = self.cache.get(text, None)

        if cached is None:
            x0, y0, x1, y1 = self.font.getbbox(
                text=text,
                stroke_width=self.stroke_width,
                anchor=self.anchor,
                direction=None if self.direction == "ltr" else self.direction
            )

            if x0 < 0:
                x1 = x1 + abs(x0)
            if y0 < 0:
                y1 = y1 + abs(x0)

            backing_image = Image.new(mode="RGBA", size=(x1, y1))
            backing_draw = ImageDraw.Draw(backing_image)

            backing_draw.text(
                (abs(x0), 0),
                text,
                anchor=self.anchor,
                direction=None if self.direction == "ltr" else self.direction,
                font=self.font,
                fill=self.fill,
                stroke_width=self.stroke_width,
                stroke_fill=self.stroke
            )
            cached = {
                "at": Coordinate(x0 if x0 < 0 else 0, y0 if y0 < 0 else 0),
                "image": backing_image
            }
            self.cache[text] = cached

        image.alpha_composite(cached["image"], (self.at + cached["at"]).tuple())


class Text(Widget):
    def __init__(self,
                 at: Coordinate,
                 value: Callable[[], str],
                 font: Any, align: str = "left",
                 direction: str = "ltr",
                 fill: Tuple = None,
                 stroke: Tuple = None,
                 stroke_width: int = 2
                 ) -> None:
        self.at = at
        self.value = value
        self.font = font
        self.anchor = anchors.get(align, align)
        self.direction = direction
        self.fill = fill if fill else (255, 255, 255)
        self.stroke = stroke if stroke else (0, 0, 0)
        self.stroke_width = stroke_width

    def draw(self, image: Image, draw: ImageDraw):
        draw.text(
            self.at.tuple(),
            self.value(),
            anchor=self.anchor,
            direction=None if self.direction == "ltr" else self.direction,
            font=self.font,
            fill=self.fill,
            stroke_width=self.stroke_width,
            stroke_fill=(0, 0, 0)
        )


anchors = {
    "left": "la",
    "right": "ra",
    "centre": "ma",
}
