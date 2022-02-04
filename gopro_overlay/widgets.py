import functools
import importlib
import os

from PIL import Image, ImageDraw

from . import icons
from .dimensions import Dimension
from .point import Coordinate

anchors = {
    "left": "la",
    "right": "ra",
    "centre": "ma",
}


class CachingText:
    def __init__(self, at, value, font, align="left", direction="ltr", fill=None):
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
                text=self.value(),
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
                self.value(),
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
    def __init__(self, at, value, font, align="left", direction="ltr", fill=None):
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


def simple_icon(at, file, size=64, invert=False):
    return icon(file, at, transform=compose(
        functools.partial(transform_resize, (size, size)),
        transform_rgba,
        transform_negative if invert else transform_identity
    ))


def transform_identity(img):
    return img


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


class ImageTranslate:
    def __init__(self, at, image):
        self.at = at
        self.image = image

    def alpha_composite(self, im, dest=(0, 0)):
        self.image.alpha_composite(im, dest=(dest[0] + self.at.x, dest[1] + self.at.y))


class DrawTranslate:
    def __init__(self, at, draw):
        self.at = at
        self.draw = draw

    def text(self, xy, text, **kwargs):
        self.draw.text(xy=(xy[0] + self.at.x, xy[1] + self.at.y), text=text, **kwargs)


class Translate:
    """Extremely rudimentary translation support!

    Translate the 'at' of child widget by this widget's location. Use in combination with a Composite
    Need to test each child type that intend to put in here, as certainly won't work for many use cases.
    """

    def __init__(self, at: Coordinate, widget):
        self.at = at
        self.widget = widget

    def draw(self, image, draw):
        ivp = ImageTranslate(self.at, image)
        dvp = DrawTranslate(self.at, draw)

        self.widget.draw(ivp, dvp)


class Scene:

    def __init__(self, widgets, dimensions: Dimension):
        self._widgets = widgets
        self._dimensions = dimensions

    def draw(self):
        image = Image.new("RGBA", (self._dimensions.x, self._dimensions.y), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        for w in self._widgets:
            w.draw(image, draw)

        return image


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), reversed(functions))
