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


class JourneyMap:
    def __init__(self, journey, extents, location, value, renderer, size=256):
        self.journey = journey
        self.extents = extents
        self.location = location
        self.value = value
        self.renderer = renderer
        self.size = size
        self.map = None
        self.image = None

    def _init_maybe(self):
        if self.map is None:
            bbox = self.extents.bounding_box
            self.map = geotiler.Map(extent=(bbox[0].lon, bbox[0].lat, bbox[1].lon, bbox[1].lat),
                                    size=(self.size, self.size))
            plots = [self.map.rev_geocode((location.lon, location.lat)) for location in self.journey.locations]
            self.image = self.renderer(self.map)
            draw = ImageDraw.Draw(self.image)
            draw.line(plots, fill=(255, 0, 0), width=4)
            draw.line(
                (0, 0, 0, self.size - 1, self.size - 1, self.size - 1, self.size - 1, 0, 0, 0),
                fill=(0, 0, 0)
            )

    def draw(self, image, draw):
        self._init_maybe()

        location = self.value()

        frame = self.image.copy()
        draw = ImageDraw.Draw(frame)
        current = self.map.rev_geocode((location.lon, location.lat))
        draw_marker(draw, current, 6)
        image.paste(frame, self.location)


def draw_marker(draw, position, size):
    draw.ellipse((position[0] - size, position[1] - size, position[0] + size, position[1] + size), fill=(0, 0, 255),
                 outline=(0, 0, 0))


class MovingMap:
    def __init__(self, location, value, azimuth, renderer, rotate=True):
        self.rotate = rotate
        self.azimuth = azimuth
        self.renderer = renderer
        self.value = value
        self.location = location

    def draw(self, image, draw):
        location = self.value()
        if location.lon is not None and location.lat is not None:
            desired = 256

            hypotenuse = int(math.sqrt((desired ** 2) * 2))

            half_width_height = (hypotenuse / 2)

            bounds = (
                half_width_height - (desired / 2),
                half_width_height - (desired / 2),
                half_width_height + (desired / 2),
                half_width_height + (desired / 2)
            )

            map = geotiler.Map(center=(location.lon, location.lat), zoom=17, size=(hypotenuse, hypotenuse))
            map_image = self.renderer(map)

            draw = ImageDraw.Draw(map_image)
            draw_marker(draw, (half_width_height, half_width_height), 6)
            azimuth = self.azimuth()
            if azimuth and self.rotate:
                azi = azimuth.to("degree").magnitude
                angle = 0 + azi if azi >= 0 else 360 + azi
                map_image = map_image.rotate(angle)

            crop = map_image.crop(bounds)

            ImageDraw.Draw(crop).line(
                (0, 0, 0, desired - 1, desired - 1, desired - 1, desired - 1, 0, 0, 0),
                fill=(0, 0, 0)
            )

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
            Text((1500, 80), lambda: f"Lat: {datasource.point().lat:0.6f}", font_metric),
            Text((1500, 120), lambda: f"Lon: {datasource.point().lon:0.6f}", font_metric),
            MovingMap((1500, 160),
                      lambda: datasource.point(),
                      lambda: datasource.azimuth(),
                      map_renderer),
            JourneyMap(
                journey=datasource.journey,
                extents=datasource.extents,
                location=(1500, 400),
                value=lambda: datasource.point(),
                renderer=map_renderer
            ),
            Text((28, 900), lambda: "Speed (mph)", font_title),
            Text((28, 922),
                 lambda: f"{datasource.speed().to('MPH').magnitude:.0f}" if datasource.speed() else "-",
                 font_metric),

            Text((28, 980), lambda: "Altitude (m)", font_title),
            Text((28, 1002),
                 lambda: f"{datasource.altitude().to('m').magnitude:.0f}" if datasource.altitude() else "-",
                 font_metric),

            Text((1500, 900), lambda: "Cadence (rpm)", font_title),
            Text((1500, 922),
                 lambda: f"{datasource.cadence().magnitude:.0f}" if datasource.cadence() else "-",
                 font_metric),

            Text((1500, 980), lambda: "Heart Rate (bpm)", font_title),
            Text((1500, 1002),
                 lambda: f"{datasource.heart_rate().magnitude:.0f}" if datasource.heart_rate() else "-",
                 font_metric),
        ]

    def draw(self):
        image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        for w in self.widgets:
            w.draw(image, draw)

        return image


if __name__ == "__main__":
    import fake

    overlay = Overlay(fake.DataSource(), geotiler.render_map)

    overlay.draw().show()
