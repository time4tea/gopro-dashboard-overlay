from typing import Callable, Any, Tuple

from PIL import Image, ImageDraw

from gopro_overlay.point import Coordinate


class CachingText:
    def __init__(self, at: Coordinate, value: Callable, font, align="left", direction="ltr", fill=None):
        self.at = at
        self.value = value
        self.font = font
        self.anchor = anchors.get(align, align)
        self.direction = direction
        self.fill = fill if fill else (255, 255, 255)
        self.cache = {}

    def draw(self, image, draw):

        text = self.value()

        if text is None:
            raise ValueError("Refusing to draw text with value of 'None'")

        cached = self.cache.get(text, None)

        if cached is None:

            x0, y0, x1, y1 = self.font.getbbox(
                text=text,
                stroke_width=2,
                anchor=self.anchor,
                direction=self.direction
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
                direction=self.direction,
                font=self.font,
                fill=self.fill,
                stroke_width=2,
                stroke_fill=(0, 0, 0)
            )
            cached = {
                "at": Coordinate(x0 if x0 < 0 else 0, y0 if y0 < 0 else 0),
                "image": backing_image
            }
            self.cache[text] = cached

        image.alpha_composite(cached["image"], (self.at + cached["at"]).tuple())


class Text:
    def __init__(self,
                 at: Coordinate,
                 value: Callable[[], str],
                 font: Any, align: str = "left",
                 direction: str = "ltr",
                 fill: Tuple = None) -> None:
        self.at = at
        self.value = value
        self.font = font
        self.anchor = anchors.get(align, align)
        self.direction = direction
        self.fill = fill if fill else (255, 255, 255)

    def draw(self, image, draw):
        draw.text(
            self.at.tuple(),
            self.value(),
            anchor=self.anchor,
            direction=self.direction,
            font=self.font,
            fill=self.fill,
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )


anchors = {
    "left": "la",
    "right": "ra",
    "centre": "ma",
}
