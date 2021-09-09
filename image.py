import datetime

import geotiler
from PIL import Image, ImageDraw, ImageFont


class Text:
    def __init__(self, location, value, font):
        self.location = location
        self.value = value
        self.font = font

    def draw(self, image, draw):
        draw.text(self.location, self.value(), fill=(255, 255, 255), font=self.font)


class Drawable:
    def __init__(self, location, drawable):
        self.location = location
        self.drawable = drawable

    def draw(self, image, draw):
        image.paste(self.drawable, self.location)


def time(clock):
    return lambda: clock().strftime("%H:%M:%S.%f")[:-3]


def date(clock):
    return lambda: clock().strftime("%Y/%m/%d")


def icon(location, file, transform=lambda x: x):
    image = Image.open(file)
    image = transform(image)
    return Drawable(location, image)


class Map:
    def __init__(self, location, value, renderer):
        self.renderer = renderer
        self.value = value
        self.location = location

    def draw(self, image, draw):
        centre = self.value()
        if centre[0] is None or centre[1] is None:
            pass
        else:
            map = geotiler.Map(center=centre, zoom=19, size=(256, 256))
            map_image = self.renderer(map)
            image.paste(map_image, self.location)


class Overlay:

    def __init__(self, datasource, map_renderer):
        self.map_renderer = map_renderer
        self.datasource = datasource
        font_title = ImageFont.truetype(font="Roboto-Medium.ttf", size=24)
        font_metric = ImageFont.truetype(font="Roboto-Medium.ttf", size=36)
        self.widgets = [
            Text((28, 36), lambda: "TIME", font_title),
            Text((28, 80), date(datasource.datetime), font_metric),
            Text((260, 80), time(datasource.datetime), font_metric),
            Text((1500, 36), lambda: "GPS INFO", font_title),
            Text((1500, 80), lambda: f"Lat: {datasource.lat()}", font_metric),
            Text((1500, 120), lambda: f"Lon: {datasource.lon()}", font_metric),
            Map((1500, 160), lambda: (datasource.lon(), datasource.lat()), map_renderer),
            Text((28, 900), lambda: "SPEED", font_title),
            # icon((100, 875), "speedometer.png"),
            # Text((28, 940), lambda: f"{datasource.speed().to('MPH'):~.3}", font_metric)
        ]

    def draw(self):
        image = Image.new("RGBA", (1920, 1080), (0, 255, 0))
        draw = ImageDraw.Draw(image)

        for w in self.widgets:
            w.draw(image, draw)

        return image


from pint import UnitRegistry

units = UnitRegistry()


class DataSource:

    # (-0.1499, +51.4972)

    def datetime(self):
        return datetime.datetime.now()

    def lat(self):
        return +51.4972

    def lon(self):
        return -0.1499

    def speed(self):
        return units.Quantity(23.5, units.mps)


if __name__ == "__main__":
    overlay = Overlay(DataSource(), geotiler.render_map)

    overlay.draw().show()
