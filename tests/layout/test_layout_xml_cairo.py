from cairo import LineCap

from gopro_overlay.layout_xml_cairo import cairo_colour, cap_from
from gopro_overlay.widgets.cairo.colour import Colour


def test_converting_colours():
    assert cairo_colour(None) is None
    assert cairo_colour((255, 255, 255)) == Colour(1.0, 1.0, 1.0)
    assert cairo_colour((0, 0, 0)) == Colour(0.0, 0.0, 0.0)
    assert cairo_colour((0, 0, 0, 0)) == Colour(0.0, 0.0, 0.0, 0.0)

def test_cap():
    assert cap_from("square") == LineCap.SQUARE
    assert cap_from("round") == LineCap.ROUND
    assert cap_from("butt") == LineCap.BUTT


