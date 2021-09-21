import math

import geotiler
from PIL import ImageDraw, ImageFont

from journey import Journey
from point import Coordinate
from widgets import Text, date, time, Scene, LeftInfoPanel, RightInfoPanel


class JourneyMap:
    def __init__(self, timeseries, at, location, renderer, size=256):
        self.journey = Journey()
        self.timeseries = timeseries

        self.at = at
        self.location = location
        self.renderer = renderer
        self.size = size
        self.map = None
        self.image = None

    def _init_maybe(self):
        if self.map is None:
            self.timeseries.process(self.journey.accept)

            bbox = self.journey.bounding_box
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

        location = self.location()

        frame = self.image.copy()
        draw = ImageDraw.Draw(frame)
        current = self.map.rev_geocode((location.lon, location.lat))
        draw_marker(draw, current, 6)
        image.paste(frame, self.at.tuple())


def draw_marker(draw, position, size):
    draw.ellipse((position[0] - size, position[1] - size, position[0] + size, position[1] + size), fill=(0, 0, 255),
                 outline=(0, 0, 0))


class MovingMap:
    def __init__(self, at, location, azimuth, renderer, rotate=True, size=256):
        self.at = at
        self.rotate = rotate
        self.azimuth = azimuth
        self.renderer = renderer
        self.location = location
        self.size = size
        self.hypotenuse = int(math.sqrt((self.size ** 2) * 2))

        self.half_width_height = (self.hypotenuse / 2)

        self.bounds = (
            self.half_width_height - (self.size / 2),
            self.half_width_height - (self.size / 2),
            self.half_width_height + (self.size / 2),
            self.half_width_height + (self.size / 2)
        )

    def draw(self, image, draw):
        location = self.location()
        if location.lon is not None and location.lat is not None:

            map = geotiler.Map(center=(location.lon, location.lat), zoom=17, size=(self.hypotenuse, self.hypotenuse))
            map_image = self.renderer(map)

            draw = ImageDraw.Draw(map_image)
            draw_marker(draw, (self.half_width_height, self.half_width_height), 6)
            azimuth = self.azimuth()
            if azimuth and self.rotate:
                azi = azimuth.to("degree").magnitude
                angle = 0 + azi if azi >= 0 else 360 + azi
                map_image = map_image.rotate(angle)

            crop = map_image.crop(self.bounds)

            ImageDraw.Draw(crop).line(
                (
                    0, 0,
                    0, self.size - 1,
                    self.size - 1, self.size - 1,
                    self.size - 1, 0,
                    0, 0
                ),
                fill=(0, 0, 0)
            )

            image.paste(crop, self.at.tuple())


class Overlay:

    def __init__(self, timeseries, map_renderer):
        self.map_renderer = map_renderer
        self.timeseries = timeseries
        self.current_entry = None

        font_title = ImageFont.truetype(font="Roboto-Medium.ttf", size=12)
        font_metric = ImageFont.truetype(font="Roboto-Medium.ttf", size=36)

        self.scene = Scene([
            Text(Coordinate(260, 36), date(lambda: self.entry.dt), font_title, align="right"),
            Text(Coordinate(260, 60), time(lambda: self.entry.dt), font_metric, align="right"),
            Text(Coordinate(1900, 36), lambda: "GPS INFO", font_title, align="right"),
            Text(Coordinate(1900, 80), lambda: f"Lat: {self.entry.point.lat:0.6f}", font_metric, align="right"),
            Text(Coordinate(1900, 120), lambda: f"Lon: {self.entry.point.lon:0.6f}", font_metric, align="right"),
            MovingMap(
                at=Coordinate(1900 - 256, 160),
                location=lambda: self.entry.point,
                azimuth=lambda: self.entry.azi,
                renderer=map_renderer
            ),
            JourneyMap(
                at=Coordinate(1900 - 256, 160 + 256 + 20),
                timeseries=timeseries,
                location=lambda: self.entry.point,
                renderer=map_renderer
            ),
            LeftInfoPanel(
                Coordinate(16, 900),
                "icons/gauge-1.png",
                lambda: "MPH",
                lambda: f"{self.entry.speed.to('MPH').magnitude:.2f}" if self.entry.speed else "-",
                font_title,
                font_metric
            ),
            LeftInfoPanel(
                Coordinate(16, 980),
                "icons/mountain.png",
                lambda: "ALT(m)",
                lambda: f"{self.entry.alt.to('m').magnitude:.2f}" if self.entry.alt else "-",
                font_title,
                font_metric
            ),
            RightInfoPanel(
                Coordinate(1900, 820),
                "icons/thermometer.png",
                lambda: "TEMP(C)",
                lambda: f"{self.entry.atemp.magnitude:.0f}" if self.entry.atemp is not None else "-",
                font_title,
                font_metric
            ),
            RightInfoPanel(
                Coordinate(1900, 900),
                "icons/gauge.png",
                lambda: "RPM",
                lambda: f"{self.entry.cad.magnitude:.0f}" if self.entry.cad else "-",
                font_title,
                font_metric
            ),
            RightInfoPanel(
                Coordinate(1900, 980),
                "icons/heartbeat.png",
                lambda: "BPM",
                lambda: f"{self.entry.hr.magnitude:.0f}" if self.entry.hr else "-",
                font_title,
                font_metric
            ),
        ])

    @property
    def entry(self):
        return self.current_entry

    def draw(self, dt):
        self.current_entry = self.timeseries.get(dt)
        return self.scene.draw()


if __name__ == "__main__":
    import fake

    timeseries = fake.fake_timeseries()

    overlay = Overlay(timeseries, geotiler.render_map)

    overlay.draw(timeseries.min).show()
