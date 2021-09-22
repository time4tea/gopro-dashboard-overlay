from PIL import ImageFont

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets import LeftInfoPanel, RightInfoPanel, simple_icon, Text, Scene
from tests.testenvironment import is_ci


# don't know why this fails only in PyCharm with AttributeError: module 'importlib' has no attribute 'resources'

def test_render_sample():
    font = ImageFont.truetype(font="Roboto-Medium.ttf", size=36)
    title_font = ImageFont.truetype(font="Roboto-Medium.ttf", size=12)
    widgets = [
        LeftInfoPanel(Coordinate(600, 600), "mountain.png", lambda: "ALT(m)", lambda: "100m", title_font, font),
        RightInfoPanel(Coordinate(1200, 600), "mountain.png", lambda: "ALT(m)", lambda: "100m", title_font, font),
        simple_icon(Coordinate(300, 300), "gauge-1.png"),
        Text(Coordinate(300, 300), lambda: "Hello", font),
    ]

    draw = Scene(widgets).draw()

    if not is_ci():
        draw.show()
