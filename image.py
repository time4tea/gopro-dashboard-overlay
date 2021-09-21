import geotiler
from PIL import ImageFont

from point import Coordinate
from widgets import Text, date, time, Scene, LeftInfoPanel, RightInfoPanel
from widgets_map import MovingMap, JourneyMap


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
