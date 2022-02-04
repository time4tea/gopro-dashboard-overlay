import math

import geotiler
from PIL import ImageDraw, Image, ImageOps

from .journey import Journey
from .privacy import NoPrivacyZone


class JourneyMap:
    def __init__(self, timeseries, at, location, renderer, size=256, corner_radius=None, opacity=0.7,
                 privacy_zone=NoPrivacyZone()):
        self.timeseries = timeseries
        self.privacy_zone = privacy_zone

        self.at = at
        self.location = location
        self.renderer = renderer
        self.corner_radius = corner_radius
        self.opacity = opacity
        self.size = size
        self.map = None
        self.image = None

    def _init_maybe(self):
        if self.map is None:
            journey = Journey()

            self.timeseries.process(journey.accept)

            bbox = journey.bounding_box
            self.map = geotiler.Map(extent=(bbox[0].lon, bbox[0].lat, bbox[1].lon, bbox[1].lat),
                                    size=(self.size, self.size))

            if self.map.zoom > 18:
                self.map.zoom = 18

            plots = [
                self.map.rev_geocode((location.lon, location.lat))
                for location in journey.locations if not self.privacy_zone.encloses(location)
            ]

            image = self.renderer(self.map)

            draw = ImageDraw.Draw(image)
            draw.line(plots, fill=(255, 0, 0), width=4)

            if self.corner_radius:
                image = rounded_corners(image, self.corner_radius, self.opacity)

                draw.rounded_rectangle(
                    (0, 0) + (self.size - 1, self.size - 1),
                    radius=self.corner_radius,
                    outline=(0, 0, 0)
                )
            else:
                draw.line(
                    (0, 0, 0, self.size - 1, self.size - 1, self.size - 1, self.size - 1, 0, 0, 0),
                    fill=(0, 0, 0)
                )

                image.putalpha(int(255 * self.opacity))

            self.image = image

    def draw(self, image, draw):
        self._init_maybe()

        location = self.location()

        frame = self.image.copy()

        draw = ImageDraw.Draw(frame)
        current = self.map.rev_geocode((location.lon, location.lat))
        draw_marker(draw, current, 6)

        image.paste(frame, self.at.tuple())


def draw_marker(draw, position, size, fill=None):
    fill = fill if fill is not None else (0, 0, 255)
    draw.ellipse((position[0] - size, position[1] - size, position[0] + size, position[1] + size),
                 fill=fill,
                 outline=(0, 0, 0))


class MovingMap:
    def __init__(self, at, location, azimuth, renderer,
                 rotate=True, size=256, zoom=17, corner_radius=None, opacity=0.7):
        self.at = at
        self.rotate = rotate
        self.azimuth = azimuth
        self.renderer = renderer
        self.location = location
        self.size = size
        self.zoom = zoom
        self.corner_radius = corner_radius
        self.opacity = opacity
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

            map = geotiler.Map(center=(location.lon, location.lat), zoom=self.zoom,
                               size=(self.hypotenuse, self.hypotenuse))
            map_image = self.renderer(map)

            draw = ImageDraw.Draw(map_image)
            draw_marker(draw, (self.half_width_height, self.half_width_height), 6)
            azimuth = self.azimuth()
            if azimuth and self.rotate:
                azi = azimuth.to("degree").magnitude
                angle = 0 + azi if azi >= 0 else 360 + azi
                map_image = map_image.rotate(angle)

            crop = map_image.crop(self.bounds)

            if self.corner_radius:
                crop = rounded_corners(crop, self.corner_radius, self.opacity)

                ImageDraw.Draw(crop).rounded_rectangle(
                    (0, 0) + (self.size - 1, self.size - 1),
                    radius=self.corner_radius,
                    outline=(0, 0, 0)
                )
            else:
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

                crop.putalpha(int(255 * self.opacity))

            image.paste(crop, self.at.tuple())


def rounded_corners(frame, radius, opacity):
    mask = Image.new('L', frame.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0) + (frame.size[0] - 1, frame.size[1] - 1), radius=radius,
                                           fill=int(opacity * 255))
    frame.putalpha(mask)
    return frame
