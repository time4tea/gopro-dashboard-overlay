import functools
import importlib
import os

from PIL import Image, ImageDraw

from . import icons

anchors = {
    "left": "la",
    "right": "ra",
    "centre": "ma",
}


class Text:
    def __init__(self, at, value, font, align="left", fill=None):
        self.at = at
        self.value = value
        self.font = font
        self.anchor = anchors[align]
        self.fill = fill if fill else (255, 255, 255)

    def draw(self, image, draw):
        draw.text(
            self.at.tuple(),
            self.value(),
            anchor=self.anchor,
            font=self.font,
            fill=self.fill,
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )


class Composite:

    def __init__(self, *widgets):
        self.widgets = widgets

    def draw(self, image, draw):
        for w in self.widgets:
            w.draw(image, draw)


class Drawable:
    def __init__(self, at, drawable):
        self.at = at
        self.drawable = drawable

    def draw(self, image, draw):
        image.alpha_composite(self.drawable, self.at.tuple())


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


def simple_icon(at, file, size=64):
    return icon(file, at, transform=compose(
        functools.partial(transform_resize, (size, size)),
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
    for i in range(0, img.size[0]):
        for j in range(0, img.size[1]):
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
