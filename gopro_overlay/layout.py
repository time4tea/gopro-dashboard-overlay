from PIL import ImageFont

from .point import Coordinate
from .privacy import NoPrivacyZone
from .widgets import Text, date, time, Scene, LeftInfoPanel, RightInfoPanel
from .widgets_map import MovingMap, JourneyMap


class Layout:

    def __init__(self, timeseries, map_renderer, privacy_zone=NoPrivacyZone()):
        self.map_renderer = map_renderer
        self.timeseries = timeseries
        self.current_entry = None

        font_title = ImageFont.truetype(font="Roboto-Medium.ttf", size=16)
        font_metric = ImageFont.truetype(font="Roboto-Medium.ttf", size=32)
        font_speed = ImageFont.truetype(font="Roboto-Medium.ttf", size=48)

        self.scene = Scene([
            Text(Coordinate(260, 36), date(lambda: self.entry.dt), font_title, align="right"),
            Text(Coordinate(260, 60), time(lambda: self.entry.dt), font_metric, align="right"),
            Text(Coordinate(1900, 36), lambda: "GPS INFO", font_title, align="right"),
            Text(Coordinate(1780, 60), lambda: f"Lat: {self.entry.point.lat:0.6f}", font_title, align="right"),
            Text(Coordinate(1900, 60), lambda: f"Lon: {self.entry.point.lon:0.6f}", font_title, align="right"),
            MovingMap(
                at=Coordinate(1900 - 256, 100),
                location=lambda: self.entry.point,
                azimuth=lambda: self.entry.azi,
                renderer=map_renderer
            ),
            JourneyMap(
                at=Coordinate(1900 - 256, 100 + 256 + 20),
                timeseries=timeseries,
                location=lambda: self.entry.point,
                renderer=map_renderer,
                privacy_zone=privacy_zone
            ),
            LeftInfoPanel(
                Coordinate(16, 900),
                "gauge-1.png",
                lambda: "MPH",
                lambda: f"{self.entry.speed.to('MPH').magnitude:.0f}" if self.entry.speed else "-",
                font_title,
                font_speed
            ),
            LeftInfoPanel(
                Coordinate(16, 980),
                "mountain.png",
                lambda: "ALT(m)",
                lambda: f"{self.entry.alt.to('m').magnitude:.1f}" if self.entry.alt else "-",
                font_title,
                font_metric
            ),
            LeftInfoPanel(
                Coordinate(220, 980),
                "slope-triangle.png",
                lambda: "SLOPE(%)",
                lambda: f"{self.entry.grad.magnitude:.1f}" if self.entry.grad else "-",
                font_title,
                font_metric
            ),

            RightInfoPanel(
                Coordinate(1900, 820),
                "thermometer.png",
                lambda: "TEMP(C)",
                lambda: f"{self.entry.atemp.magnitude:.0f}" if self.entry.atemp is not None else "-",
                font_title,
                font_metric
            ),
            RightInfoPanel(
                Coordinate(1900, 900),
                "gauge.png",
                lambda: "RPM",
                lambda: f"{self.entry.cad.magnitude:.0f}" if self.entry.cad else "-",
                font_title,
                font_metric
            ),
            RightInfoPanel(
                Coordinate(1900, 980),
                "heartbeat.png",
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
