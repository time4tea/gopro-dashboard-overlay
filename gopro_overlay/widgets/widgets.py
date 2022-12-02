import functools
import importlib
import os
import math
from typing import Tuple, Any

from PIL import Image, ImageDraw

from gopro_overlay import icons
from gopro_overlay.dimensions import Dimension
from gopro_overlay.functional import compose
from gopro_overlay.point import Coordinate


class EmptyDrawable:
    def draw(self, image, draw):
        pass


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

    def _txy(self, xy):
        return xy[0] + self.at.x, xy[1] + self.at.y

    def alpha_composite(self, im, dest=(0, 0), source=(0, 0)):
        self.image.alpha_composite(im, dest=self._txy(dest), source=source)

    def paste(self, img, box):
        self.image.paste(img, box=self._txy(box))


class DrawTranslate:
    def __init__(self, at, draw):
        self.at = at
        self.draw = draw

    def _txy(self, xy):
        return xy[0] + self.at.x, xy[1] + self.at.y

    def text(self, xy, text, **kwargs):
        self.draw.text(xy=self._txy(xy), text=text, **kwargs)

    def rounded_rectangle(self, xy, *args, **kwargs):
        self.draw.rounded_rectangle([self._txy(pair) for pair in xy], *args, **kwargs)

    def point(self, xy, **kwargs):
        self.draw.point(xy=self._txy(xy), **kwargs)

    def rectangle(self, xy, *args, **kwargs):
        self.draw.rectangle([self._txy(pair) for pair in xy], *args, **kwargs)

    def line(self, xy, *args, **kwargs):
        self.draw.line([self._txy(pair) for pair in xy], *args, **kwargs)

    def ellipse(self, xy, *args, **kwargs):
        self.draw.ellipse([self._txy(pair) for pair in xy], *args, **kwargs)

    def arc(self, xy, *args, **kwargs):
        self.draw.arc([self._txy(pair) for pair in xy], *args, **kwargs)

    def pieslice(self, xy, *args, **kwargs):
        self.draw.pieslice([self._txy(pair) for pair in xy], *args, **kwargs)

    def polygon(self, xy, *args, **kwargs):
        self.draw.polygon([self._txy(pair) for pair in xy], *args, **kwargs)


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


class Frame:
    """
    A clipping bordered frame that also makes a child controllably transparent
    """

    def __init__(self,
                 dimensions: Dimension,
                 opacity: float = 1.0,
                 corner_radius: int = 0,
                 outline: Tuple = None,
                 fill: Tuple = None,
                 child: Any = EmptyDrawable(),
                 fade_out: int = 0) -> None:
        self.child = child
        self.corner_radius = corner_radius
        self.fill = fill
        self.outline = outline
        self.opacity = opacity
        self.dimensions = dimensions
        self.mask = None
        self.fade_out = fade_out

    def _maybe_init(self):
        if self.mask is None:
            self.mask = Image.new('L', (self.dimensions.x, self.dimensions.y), 0)
            ImageDraw.Draw(self.mask).rounded_rectangle(
                (0, 0) + (self.dimensions.x - 1, self.dimensions.y - 1),
                radius=self.corner_radius,
                fill=int(self.opacity * 255)
            )
            if self.fade_out > 0:
                self._init_fadeout()

    def _init_fadeout(self):
            for y in range(self.dimensions.y):
                for x in range(self.dimensions.x):
                    distance_to_center = math.sqrt((x - self.dimensions.x/2) ** 2 + (y - self.dimensions.y/2) ** 2)
                    radius = min(self.dimensions.x, self.dimensions.y) / 2
                    distance_from_side = 1 - (distance_to_center / radius)
                    distance_from_side = min(x, min(y, min(self.dimensions.x - x, self.dimensions.y - y))) / radius
                    if self.corner_radius == 0:
                        # no radius defined, we will use distance_from_side
                        distance_from_corner_radius = distance_from_side
                    else:
                        # we can use a more complex formula for getting the distance from corner_radius, but for simplicity we will use this one
                        # it will lead to more straight lines instead of rounded corners
                        outer_radius = math.sqrt(self.corner_radius ** 2 + self.corner_radius ** 2) - self.corner_radius
                        rounder_radius = math.sqrt((self.dimensions.x/2) ** 2 + (self.dimensions.y/2) ** 2) - outer_radius
                        distance_from_corner_radius = (rounder_radius - distance_to_center) / rounder_radius
                    fade_out_percents = max(0.01, min(1.0, self.fade_out / radius))
                    self.mask.putpixel((x, y), int(min(1.0, min(distance_from_side, distance_from_corner_radius) / fade_out_percents) * 255 * self.opacity))

    def draw(self, image, draw):
        self._maybe_init()

        rect = Image.new('RGBA', (self.dimensions.x, self.dimensions.y), self.fill)
        rect_draw = ImageDraw.Draw(rect)

        self.child.draw(rect, rect_draw)

        if self.outline is not None:
            rect_draw.rounded_rectangle(
                ((0, 0), (self.dimensions.x - 1, self.dimensions.y - 1)),
                radius=self.corner_radius,
                outline=self.outline
            )

        rect.putalpha(self.mask)

        image.alpha_composite(rect, (0, 0))


class Scene:

    def __init__(self, dimensions: Dimension, widgets, ):
        self._widgets = widgets
        self._dimensions = dimensions

    def draw(self):
        image = Image.new("RGBA", (self._dimensions.x, self._dimensions.y), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        for w in self._widgets:
            w.draw(image, draw)

        return image
