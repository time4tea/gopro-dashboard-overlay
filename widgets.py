import functools

from PIL import Image, ImageDraw, ImageFont


class Text:
    def __init__(self, at, value, font):
        self.at = at
        self.value = value
        self.font = font

    def draw(self, image, draw):
        draw.text(self.at, self.value(), font=self.font, fill=(255, 255, 255), stroke_width=2,
                  stroke_fill=(0, 0, 0))


class Drawable:
    def __init__(self, at, drawable):
        self.at = at
        self.drawable = drawable

    def draw(self, image, draw):
        # doesn't do proper alpha composite - draw icons first!
        image.paste(self.drawable, self.at)


def time(clock):
    return lambda: clock().strftime("%H:%M:%S.%f")[:-3]


def date(clock):
    return lambda: clock().strftime("%Y/%m/%d")


def icon(file, at, transform=lambda x: x):
    return Drawable(at, transform(Image.open(file)))


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
    widgets = [
        icon("icons/gauge-1.png", (300, 300), transform=compose(
            functools.partial(transform_resize, (64, 64)),
            transform_rgba,
            transform_negative
        )),
        Text((300, 300), lambda: "Hello", font),
    ]

    Scene(widgets).draw().show()
