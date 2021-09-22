import functools
import importlib
import os

from PIL import Image, ImageDraw, ImageFont

from . import icons
from .point import Coordinate

anchors = {
    "left": "la",
    "right": "ra"
}


class Text:
    def __init__(self, at, value, font, align="left"):
        self.at = at
        self.value = value
        self.font = font
        self.anchor = anchors[align]

    def draw(self, image, draw):
        draw.text(
            self.at.tuple(),
            self.value(),
            anchor=self.anchor,
            font=self.font,
            fill=(255, 255, 255),
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )


class Drawable:
    def __init__(self, at, drawable):
        self.at = at
        self.drawable = drawable

    def draw(self, image, draw):
        image.alpha_composite(self.drawable, self.at.tuple())


class RightInfoPanel:

    def __init__(self, at, icon, title, value, title_font, value_font):
        self.value = value
        self.widgets = [
            Text(at + Coordinate(-70, 0), title, title_font, align="right"),
            simple_icon(at + Coordinate(-64, 0), icon),
            Text(at + Coordinate(-70, 18), value, value_font, align="right"),
        ]

    def draw(self, image, draw):
        for w in self.widgets:
            w.draw(image, draw)


class LeftInfoPanel:

    def __init__(self, at, icon, title, value, title_font, value_font):
        self.value = value
        self.widgets = [
            Text(at + Coordinate(70, 0), title, title_font),
            simple_icon(at + Coordinate(0, 0), icon),
            Text(at + Coordinate(70, 18), value, value_font),
        ]

    def draw(self, image, draw):
        for w in self.widgets:
            w.draw(image, draw)


def time(clock):
    return lambda: clock().strftime("%H:%M:%S.%f")[:-5]


def date(clock):
    return lambda: clock().strftime("%Y/%m/%d")


def icon(file, at, transform=lambda x: x):
    if os.path.exists(file):
        image = Image.open(file)
    else:
        with importlib.resources.path(icons, file) as f:
            image = Image.open(f)

    return Drawable(at, transform(image))


def simple_icon(at, file):
    return icon(file, at, transform=compose(
        functools.partial(transform_resize, (64, 64)),
        transform_rgba,
        transform_negative
    ))


def transform_resize(target, img):
    return img.resize(target)


def transform_rgba(img):
    return img.convert("RGBA") if img.mode == "P" else img


def transform_negative(img):
    if img.mode != "RGBA":
        raise ValueError(f"I only work on RGBA, not {img.mode}")
    for i in range(0, img.size[0] - 1):
        for j in range(0, img.size[1] - 1):
            pixel = img.getpixel((i, j))
            img.putpixel((i, j), (255 - pixel[0], 255 - pixel[1], 255 - pixel[2], pixel[3]))
    return img


class Scene:

    def __init__(self, widgets, dimensions=None):
        self._widgets = widgets
        self._dimensions = dimensions if dimensions else (1920, 1080)

    def draw(self):
        image = Image.new("RGBA", self._dimensions, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        for w in self._widgets:
            w.draw(image, draw)

        return image


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), reversed(functions))


if __name__ == "__main__":
    font = ImageFont.truetype(font="Roboto-Medium.ttf", size=36)
    title_font = ImageFont.truetype(font="Roboto-Medium.ttf", size=12)
    widgets = [
        LeftInfoPanel(Coordinate(600, 600), "icons/mountain.png", lambda: "ALT(m)", lambda: "100m", title_font, font),
        RightInfoPanel(Coordinate(1200, 600), lambda: "ALT(m)", "icons/mountain.png", lambda: "100m", title_font, font),
        simple_icon(Coordinate(300, 300), "icons/gauge-1.png"),
        Text(Coordinate(300, 300), lambda: "Hello", font),
    ]

    Scene(widgets).draw().show()
