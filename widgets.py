from PIL import Image, ImageDraw


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
        image.paste(self.drawable, self.at)


def time(clock):
    return lambda: clock().strftime("%H:%M:%S.%f")[:-3]


def date(clock):
    return lambda: clock().strftime("%Y/%m/%d")


def icon(location, file, transform=lambda x: x):
    image = Image.open(file)
    image = transform(image)
    return Drawable(location, image)


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
