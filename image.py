import bisect
import math

import geotiler
from PIL import Image, ImageDraw, ImageFont

from journey import Journey
from widgets import Text, date, time, Scene


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
        image.paste(frame, self.at)


def draw_marker(draw, position, size):
    draw.ellipse((position[0] - size, position[1] - size, position[0] + size, position[1] + size), fill=(0, 0, 255),
                 outline=(0, 0, 0))


class MovingMap:
    def __init__(self, at, location, azimuth, renderer, rotate=True):
        self.at = at
        self.rotate = rotate
        self.azimuth = azimuth
        self.renderer = renderer
        self.location = location

    def draw(self, image, draw):
        location = self.location()
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

            image.paste(crop, self.at)


class SparkLine:
    import matplotlib
    matplotlib.use("Agg")

    def __init__(self, at, timeseries, dt):
        self.at = at
        self.timeseries = timeseries
        self.dt = dt
        self.cadences = None
        self.dts = None

    def _maybe_init(self):

        self.cadences = []
        self.dts = []

        def process(entry):
            self.cadences.append(entry.cad.magnitude if entry.cad else 0)
            self.dts.append(entry.dt)

        if not self.cadences:
            self.timeseries.process(process)

    def draw(self, image, draw):
        import matplotlib.pyplot as plt

        self._maybe_init()

        data = self.cadences

        fig, ax = plt.subplots(1, 1, figsize=(4, 0.25))
        ax.plot(data, "r")
        for k, v in ax.spines.items():
            v.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])

        current_dt = self.dt()
        dt_index = bisect.bisect_right(self.dts, current_dt)

        plt.plot(dt_index, data[dt_index], 'wo')

        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        ax.fill_between(range(len(data)), data, len(data) * [min(data)], color="red", alpha=0.2)

        fig.canvas.draw()

        # PIL Conversion...
        sparkline = Image.frombytes("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba().tobytes())

        image.paste(sparkline, self.at)


class Overlay:

    def __init__(self, timeseries, map_renderer):
        self.map_renderer = map_renderer
        self.timeseries = timeseries
        self.current_entry = None

        font_title = ImageFont.truetype(font="Roboto-Medium.ttf", size=24)
        font_metric = ImageFont.truetype(font="Roboto-Medium.ttf", size=36)

        self.scene = Scene([
            Text((28, 36), lambda: "TIME", font_title),
            Text((28, 80), date(lambda: self.entry.dt), font_metric),
            Text((260, 80), time(lambda: self.entry.dt), font_metric),
            Text((1500, 36), lambda: "GPS INFO", font_title),
            Text((1500, 80), lambda: f"Lat: {self.entry.point.lat:0.6f}", font_metric),
            Text((1500, 120), lambda: f"Lon: {self.entry.point.lon:0.6f}", font_metric),
            MovingMap(
                at=(1500, 160),
                location=lambda: self.entry.point,
                azimuth=lambda: self.entry.azi,
                renderer=map_renderer
            ),
            JourneyMap(
                at=(1500, 400),
                timeseries=timeseries,
                location=lambda: self.entry.point,
                renderer=map_renderer
            ),
            Text((28, 900), lambda: "Speed (mph)", font_title),
            Text((28, 922),
                 lambda: f"{self.entry.speed.to('MPH').magnitude:.0f}" if self.entry.speed else "-",
                 font_metric),

            Text((28, 980), lambda: "Altitude (m)", font_title),
            Text((28, 1002),
                 lambda: f"{self.entry.alt.to('m').magnitude:.0f}" if self.entry.alt else "-",
                 font_metric),

            Text((1500, 900), lambda: "Cadence (rpm)", font_title),
            Text((1500, 922),
                 lambda: f"{self.entry.cad.magnitude:.0f}" if self.entry.cad else "-",
                 font_metric),
            SparkLine((1500, 1000),
                      timeseries=timeseries,
                      dt=lambda: self.entry.dt
                      ),
            Text((1500, 980), lambda: "Heart Rate (bpm)", font_title),
            Text((1500, 1002),
                 lambda: f"{self.entry.hr.magnitude:.0f}" if self.entry.hr else "-",
                 font_metric),
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
