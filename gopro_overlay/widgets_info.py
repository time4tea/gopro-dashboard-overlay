from gopro_overlay.point import Coordinate
from gopro_overlay.widgets import Composite, Text, simple_icon


class BigMetric:

    def __init__(self, at, title, value, font):
        self.widget = Composite(
            Text(at + Coordinate(0, 0), title, font),
            Text(at + Coordinate(0, 0), value, font.font_variant(size=160)),
        )

    def draw(self, image, draw):
        self.widget.draw(image, draw)


class RightInfoPanel:

    def __init__(self, at, icon, title, value, title_font, value_font):
        self.value = value
        self.widget = Composite(
            Text(at + Coordinate(-70, 0), title, title_font, align="right"),
            simple_icon(at + Coordinate(-64, 0), icon),
            Text(at + Coordinate(-70, 18), value, value_font, align="right"),
        )

    def draw(self, image, draw):
        self.widget.draw(image, draw)


class LeftInfoPanel:

    def __init__(self, at, icon, title, value, title_font, value_font):
        self.value = value
        self.widget = Composite(
            Text(at + Coordinate(70, 0), title, title_font),
            simple_icon(at + Coordinate(0, 0), icon),
            Text(at + Coordinate(70, 18), value, value_font),
        )

    def draw(self, image, draw):
        self.widget.draw(image, draw)

