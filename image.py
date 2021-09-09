import datetime
import math

import geotiler
from PIL import Image, ImageDraw, ImageFont


class Text:
    def __init__(self, location, value, font):
        self.location = location
        self.value = value
        self.font = font

    def draw(self, image, draw):
        draw.text(self.location, self.value(), font=self.font, fill=(255, 255, 255), stroke_width=2,
                  stroke_fill=(0, 0, 0))


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
    def __init__(self, location, value, azimuth, renderer):
        self.azimuth = azimuth
        self.renderer = renderer
        self.value = value
        self.location = location

    def draw(self, image, draw):
        centre = self.value()
        if centre[0] is not None and centre[1] is not None:
            desired = 256

            hypotenuse = int(math.sqrt((desired ** 2) * 2))

            half_width_height = (hypotenuse / 2)

            bounds = (
                half_width_height - (desired / 2),
                half_width_height - (desired / 2),
                half_width_height + (desired / 2),
                half_width_height + (desired / 2)
            )

            map = geotiler.Map(center=centre, zoom=17, size=(hypotenuse, hypotenuse))
            map_image = self.renderer(map)

            draw = ImageDraw.Draw(map_image)
            draw.ellipse((half_width_height - 3, half_width_height - 3, half_width_height + 3, half_width_height + 3),
                         fill=(255, 0, 0), outline=(0, 0, 0))
            azimuth = self.azimuth()
            if azimuth:
                azi = azimuth.to("degree").magnitude
                angle = 0 + azi if azi >= 0 else 360 + azi
                map_image = map_image.rotate(angle)

            crop = map_image.crop(bounds)

            ImageDraw.Draw(crop).line((0, 0, 0, desired - 1, desired - 1, desired - 1, desired - 1, 0),
                                      fill=(255, 255, 255))

            image.paste(crop, self.location)


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
            Text((1500, 80), lambda: f"Lat: {datasource.lat():0.6f}", font_metric),
            Text((1500, 120), lambda: f"Lon: {datasource.lon():0.6f}", font_metric),
            Map((1500, 160), lambda: (datasource.lon(), datasource.lat()), lambda: datasource.azimuth(), map_renderer),
            Text((28, 900), lambda: "SPEED", font_title),
            # icon((100, 875), "speedometer.png"),
            Text((28, 940), lambda: f"{datasource.speed().to('MPH'):~.3}" if datasource.speed() else "Unknown",
                 font_metric),
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

    def azimuth(self):
        return units.Quantity(90, units.degrees)


if __name__ == "__main__":
    overlay = Overlay(DataSource(), geotiler.render_map)

    overlay.draw().show()
