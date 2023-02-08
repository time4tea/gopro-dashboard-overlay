import math
from typing import Callable

import geotiler
from PIL import ImageDraw, Image

from gopro_overlay.dimensions import Dimension
from gopro_overlay.framemeta import FrameMeta
from gopro_overlay.journey import Journey
from gopro_overlay.log import log
from gopro_overlay.point import Point
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.rdp import rdp
from gopro_overlay.widgets.widgets import Widget


class PerceptibleMovementCheck:

    def __init__(self, always=False):
        self.always = always
        self.last_location = None


    def moved(self, map, location):

        if self.always:
            return True

        location_of_centre_pixel = map.geocode((map.size[0] / 2, map.size[1] / 2))
        location_of_one_pixel_away = map.geocode(((map.size[0] / 2) + 1, (map.size[1] / 2) + 1))

        x_resolution = abs(location_of_one_pixel_away[0] - location_of_centre_pixel[0])
        y_resolution = abs(location_of_one_pixel_away[1] - location_of_centre_pixel[1])

        if self.last_location is not None:
            x_diff = abs(self.last_location.lon - location.lon)
            y_diff = abs(self.last_location.lat - location.lat)

            if x_diff < x_resolution and y_diff < y_resolution:
                return False

        self.last_location = location
        return True


class MaybeRoundedBorder:

    def __init__(self, size, corner_radius, opacity):
        self.opacity = opacity
        self.corner_radius = corner_radius
        self.size = size
        self.mask = None

    def rounded(self, image):

        draw = ImageDraw.Draw(image)

        if self.corner_radius:
            if self.mask is None:
                self.mask = self.generate_mask()

            image.putalpha(self.mask)

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

        return image

    def generate_mask(self):
        mask = Image.new('L', (self.size, self.size), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0) + (self.size - 1, self.size - 1), radius=self.corner_radius,
                                               fill=int(self.opacity * 255))
        return mask


class JourneyMap(Widget):
    def __init__(self, timeseries, at, location, renderer, size=256, corner_radius=None, opacity=0.7,
                 privacy_zone=NoPrivacyZone()):
        self.timeseries = timeseries
        self.privacy_zone = privacy_zone
        self.at = at
        self.location = location
        self.renderer = renderer
        self.size = size
        self.border = MaybeRoundedBorder(size=size, corner_radius=corner_radius, opacity=opacity)
        self.map = None
        self.image = None

    def _init_maybe(self):
        if self.map is None:
            journey = Journey()

            self.timeseries.process(journey.accept)

            bbox = journey.bounding_box
            self.map = geotiler.Map(extent=(bbox.min.lon, bbox.min.lat, bbox.max.lon, bbox.max.lat),
                                    size=(self.size, self.size))

            if self.map.zoom > 18:
                self.map.zoom = 18

            plots = rdp(
                points=[
                    self.map.rev_geocode((location.lon, location.lat))
                    for location in journey.locations if not self.privacy_zone.encloses(location)
                ],
                epsilon=1
            )

            image = self.renderer(self.map)

            draw = ImageDraw.Draw(image)
            draw.line(plots, fill=(255, 0, 0), width=4)

            self.image = self.border.rounded(image)

    def draw(self, image: Image, draw: ImageDraw):
        self._init_maybe()

        location = self.location()

        frame = self.image.copy()

        draw = ImageDraw.Draw(frame)
        current = self.map.rev_geocode((location.lon, location.lat))
        draw_marker(draw, current, 6)

        image.alpha_composite(frame, self.at.tuple())


def draw_marker(draw, position, size, fill=None):
    fill = fill if fill is not None else (0, 0, 255)
    draw.ellipse([(position[0] - size, position[1] - size), (position[0] + size, position[1] + size)],
                 fill=fill,
                 outline=(0, 0, 0))


class MovingMap(Widget):
    def __init__(self, at, location, azimuth, renderer,
                 rotate=True, size=256, zoom=17, corner_radius=None, opacity=0.7, always_redraw=False):
        self.at = at
        self.rotate = rotate
        self.azimuth = azimuth
        self.renderer = renderer
        self.location = location
        self.size = size
        self.zoom = zoom
        self.hypotenuse = int(math.sqrt((self.size ** 2) * 2))

        self.half_width_height = (self.hypotenuse / 2)

        self.bounds = (
            self.half_width_height - (self.size / 2),
            self.half_width_height - (self.size / 2),
            self.half_width_height + (self.size / 2),
            self.half_width_height + (self.size / 2)
        )
        self.perceptible = PerceptibleMovementCheck(always_redraw)
        self.border = MaybeRoundedBorder(size=size, corner_radius=corner_radius, opacity=opacity)
        self.cached = None

    def _redraw(self, map):
        image = self.renderer(map)

        draw = ImageDraw.Draw(image)
        draw_marker(draw, (self.half_width_height, self.half_width_height), 6)
        azimuth = self.azimuth()
        if azimuth and self.rotate:
            azi = azimuth.to("degree").magnitude
            angle = 0 + azi if azi >= 0 else 360 + azi
            image = image.rotate(angle)

        crop = image.crop(self.bounds)

        return self.border.rounded(crop)

    def draw(self, image: Image, draw: ImageDraw):
        location = self.location()
        if location.lon is not None and location.lat is not None:

            map = geotiler.Map(center=(location.lon, location.lat), zoom=self.zoom,
                               size=(self.hypotenuse, self.hypotenuse))

            if self.perceptible.moved(map, location):
                self.cached = self._redraw(map)

            image.alpha_composite(self.cached, self.at.tuple())


def view_window(size, d):
    def f(n):
        start = max(0, min(d - size, n - int(size / 2)))
        end = start + size
        return start, end

    return f


class MovingJourneyMap(Widget):

    def __init__(self, timeseries, privacy_zone, location, size, zoom, renderer):
        self.privacy_zone = privacy_zone
        self.timeseries = timeseries
        self.size = size
        self.renderer = renderer
        self.zoom = zoom
        self.location = location

        self.cached_map_image = None
        self.cached_map = None

    def _redraw(self):
        journey = Journey()
        self.timeseries.process(journey.accept)

        bbox = journey.bounding_box

        map = geotiler.Map(
            extent=(
                bbox.min.lon, bbox.min.lat,
                bbox.max.lon, bbox.max.lat
            ),
            zoom=self.zoom
        )

        # add self.size / 2 to each side of the map, so adding self.size overall
        map.size = (map.size[0] + self.size), (map.size[1] + self.size)

        log(f"{self.__class__.__name__} Rendering backing map ({map.size}) (can be slow)")

        map_image = self.renderer(map)

        log(f"... done")

        plots = [
            map.rev_geocode((location.lon, location.lat))
            for location in journey.locations if not self.privacy_zone.encloses(location)
        ]

        draw = ImageDraw.Draw(map_image)
        draw.line(plots, fill=(255, 0, 0), width=4)

        return map, map_image

    def draw(self, image: Image, draw: ImageDraw):
        if self.cached_map is None:
            self.cached_map, self.cached_map_image = self._redraw()

        location = self.location()
        if location.lon is not None and location.lat is not None:
            current_position_in_big_map = self.cached_map.rev_geocode((location.lon, location.lat))

            map_size = self.cached_map_image.size

            lr = view_window(self.size, map_size[0])(int(current_position_in_big_map[0]))
            tb = view_window(self.size, map_size[1])(int(current_position_in_big_map[1]))

            image.alpha_composite(self.cached_map_image, (0, 0), source=(lr[0], tb[0], lr[1], tb[1]))
            draw_marker(draw, (int(self.size / 2), int(self.size / 2)), 6)


class OutLine:
    def __init__(self, fill, fill_width, outline, outline_width):
        self.outline_width = outline_width
        self.outline = outline
        self.fill_width = fill_width
        self.fill = fill

    def draw(self, draw, points):
        if self.outline_width > 0:
            draw.line(points, fill=self.outline, width=self.fill_width)

        draw.line(points, fill=self.fill, width=self.fill_width - self.outline_width)


class Circuit(Widget):
    def __init__(self, dimensions: Dimension, framemeta: FrameMeta, location: Callable[[], Point],
                 privacy_zone=NoPrivacyZone(),
                 fill=(255, 0, 0), fill_width=4, outline=(255, 255, 255), outline_width=2):
        self.framemeta = framemeta
        self.location = location
        self.dimensions = dimensions
        self.privacy_zone = privacy_zone

        self.outline = OutLine(fill=fill, fill_width=fill_width, outline=outline, outline_width=outline_width)

        self.image = None
        self.bbox = None
        self.size = None

    def scale(self, point):
        x = int((((point.lat - self.bbox.min.lat) / self.size.x) * self.dimensions.x) + self.dimensions.x / 20)
        y = int((((point.lon - self.bbox.min.lon) / self.size.y) * self.dimensions.y) + self.dimensions.y / 20)
        return x, y

    def draw(self, image: Image, draw: ImageDraw):
        if self.image is None:
            journey = Journey()
            self.framemeta.process(journey.accept)

            self.bbox = journey.bounding_box
            self.size = self.bbox.size() * 1.1

            self.image = Image.new("RGBA", self.dimensions.tuple(), (0, 0, 0, 0))
            draw = ImageDraw.Draw(self.image)

            points = [self.scale(p) for p in journey.locations if not self.privacy_zone.encloses(p)]

            self.outline.draw(draw, rdp(points, 1))

        location = self.location()
        frame = self.image.copy()
        draw = ImageDraw.Draw(frame)

        if not self.privacy_zone.encloses(location):
            draw_marker(draw, self.scale(location), 6)

        image.alpha_composite(frame, (0, 0))
