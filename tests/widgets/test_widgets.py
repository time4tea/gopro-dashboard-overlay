import pytest
from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.gpmf import GPSFix
from gopro_overlay.layout import BigMetric, gps_info
from gopro_overlay.layout_components import text, metric
from gopro_overlay.point import Coordinate
from gopro_overlay.timing import PoorTimer
from gopro_overlay.units import units
from gopro_overlay.widgets.gps import GPSLock
from gopro_overlay.widgets.info import ComparativeEnergy
from gopro_overlay.widgets.map import OutLine
from gopro_overlay.widgets.text import CachingText, Text
from gopro_overlay.widgets.widgets import simple_icon, Scene, Composite, Translate, Widget, SimpleFrameSupplier
from tests.widgets import test_widgets_setup
from tests.approval import approve_image
from tests.testenvironment import is_make

font = test_widgets_setup.font
ts = test_widgets_setup.ts


@pytest.mark.gfx
@approve_image
def test_render_icon():
    return time_rendering("icon", widgets=[
        simple_icon(Coordinate(50, 50), "gauge-1.png", invert=True),
    ])


@pytest.mark.gfx
@approve_image
def test_render_text():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font)])


@pytest.mark.gfx
@approve_image
def test_render_text_colour():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font, fill=(255, 255, 0))])


@pytest.mark.gfx
@approve_image
def test_render_text_vertical():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font, direction="ttb", align="lt")])


@pytest.mark.gfx
@approve_image
def test_render_caching_text_vertical():
    return time_rendering("simple text", [Text(Coordinate(50, 50), lambda: "Hello", font, direction="ttb", align="lt")])


@pytest.mark.gfx
@approve_image
def test_render_caching_text_small():
    return time_rendering("simple text (cached)", [CachingText(Coordinate(50, 50), lambda: "Hello", font)])


@pytest.mark.gfx
@approve_image
def test_render_text_big():
    # 15ms target to beat
    return time_rendering("big text",
                          [Text(Coordinate(50, 50), lambda: "Hello", font.font_variant(size=160))])


@pytest.mark.gfx
@approve_image
def test_render_caching_text_big():
    # Avg: 0.00014, Rate: 6,966.58
    return time_rendering("big text (cached)",
                          [CachingText(Coordinate(50, 50), lambda: "Hello", font.font_variant(size=160))])


@pytest.mark.gfx
@approve_image
def test_render_gps_info():
    # Avg: 0.00645, Rate: 155.05
    entry = ts.get(ts.min)
    return time_rendering(
        name="gps info",
        widgets=[gps_info(Coordinate(400, 10), lambda: entry, font)]
    )


@pytest.mark.gfx
@approve_image
def test_render_big_metric():
    # Avg: 0.00026, Rate: 3,871.63
    return time_rendering(name="big speed", widgets=[
        BigMetric(Coordinate(10, 10), title=lambda: "MPH", value=lambda: "27", font_title=font,
                  font_metric=font.font_variant(size=160))
    ])


@pytest.mark.gfx
@approve_image
def test_render_comparative_energy():
    # Avg: 0.00148, Rate: 676.70
    speed = units.Quantity(25, units.mph)

    return time_rendering(name="comparative energy",
                          dimensions=Dimension(x=1300, y=200),
                          widgets=[
                              Translate(
                                  Coordinate(10, 50),
                                  ComparativeEnergy(
                                      font=font,
                                      speed=lambda: speed,
                                      person=units.Quantity(60, units.kg),
                                      bike=units.Quantity(12, units.kg),
                                      car=units.Quantity(2678, units.kg),
                                      van=units.Quantity(3500, units.kg)
                                  )
                              )
                          ])


@pytest.mark.gfx
@approve_image
def test_text_component():
    return time_rendering(name="text", widgets=[
        text(at=Coordinate(100, 100), value=lambda: "String", font=font.font_variant(size=50))
    ])


@pytest.mark.gfx
@approve_image
def test_metric_component():
    return time_rendering(name="text", widgets=[
        metric(
            at=Coordinate(100, 100),
            entry=lambda: ts.get(ts.min),
            accessor=lambda e: e.speed,
            formatter=lambda v: format(v, ".1f"),
            font=font.font_variant(size=160),
        )
    ])


@pytest.mark.gfx
@approve_image
def test_composite_viewport():
    return time_rendering(name="viewport", widgets=[
        Translate(
            Coordinate(330, 130),
            Composite(
                text(at=Coordinate(0, 0), cache=True, value=lambda: "String", font=font.font_variant(size=50)),
                simple_icon(Coordinate(0, 50), "gauge-1.png", invert=True),
            )
        )
    ])


class OutlineWidget(Widget):

    def __init__(self, outline, points):
        self.points = points
        self.outline = outline

    def draw(self, image: Image, draw: ImageDraw):
        self.outline.draw(draw, self.points)


@approve_image
def test_out_line():
    points = [
        (0, 0), (100, 100),
        (100, 100), (200, 0),
        (200, 0), (300, 100),
    ]
    return time_rendering(name="viewport", widgets=[
        OutlineWidget(
            outline=OutLine(fill=(255, 0, 0), fill_width=10, outline=None, outline_width=0),
            points=points
        ),
        Translate(
            Coordinate(0, 100),
            OutlineWidget(
                outline=OutLine(fill=(255, 0, 0), fill_width=10, outline=(255, 255, 255), outline_width=2),
                points=points
            )
        )
    ])


def gps_lock_with_fix(fix):
    return GPSLock(
        fix=lambda: fix.value,
        lock_no=Text(at=Coordinate(0, 0), value=lambda: "No Lock", font=font),
        lock_unknown=Text(at=Coordinate(0, 0), value=lambda: "Unknown", font=font),
        lock_2d=Text(at=Coordinate(0, 0), value=lambda: "Lock 2D", font=font),
        lock_3d=Text(at=Coordinate(0, 0), value=lambda: "Lock 3D", font=font),
    )


@approve_image
def test_gps_lock():
    return time_rendering(name="gps lock", widgets=[
        Translate(Coordinate(0, 0), gps_lock_with_fix(GPSFix.NO)),
        Translate(Coordinate(0, 128), gps_lock_with_fix(GPSFix.UNKNOWN)),
        Translate(Coordinate(128, 0), gps_lock_with_fix(GPSFix.LOCK_2D)),
        Translate(Coordinate(128, 128), gps_lock_with_fix(GPSFix.LOCK_3D)),
    ])


def time_rendering(name, widgets, dimensions: Dimension = Dimension(x=600, y=300), repeat=1):
    timer = PoorTimer(name)

    supplier = SimpleFrameSupplier(dimensions)
    scene = Scene(widgets)
    draw = None
    for i in range(0, repeat):
        draw = timer.time(lambda: scene.draw(supplier.drawing_frame()))

    if not is_make():
        draw.show()

    print(timer)
    return draw
