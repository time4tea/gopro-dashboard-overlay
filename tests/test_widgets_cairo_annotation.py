import pytest

from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.cairo.angle import Angle
from gopro_overlay.widgets.cairo.annotation import EllipticAnnotation, AnnotationMode
from gopro_overlay.widgets.cairo.colour import BLACK
from gopro_overlay.widgets.cairo.ellipse import EllipseParameters
from gopro_overlay.widgets.cairo.face import ToyFontFace
from gopro_overlay.widgets.cairo.tick import TickParameters
from tests.approval import approve_image
from tests.test_widgets_cairo import cairo_widget_test


@pytest.mark.cairo
@approve_image
def test_annotation():
    sectors = 17
    step = Angle(degrees=254) / sectors

    return cairo_widget_test(
        widget=EllipticAnnotation(
            ellipse=EllipseParameters(Coordinate(x=0.5, y=0.5), major_curve=1.0 / 0.41, minor_radius=0.41, angle=0),
            tick=TickParameters(step=(Angle.semicircle() / 12) / 2.0, first=1, skipped=2),
            colour=BLACK,
            face=ToyFontFace("arial"),
            mode=AnnotationMode.MovedInside,
            texts=[str(x) for x in range(0, 180, 10)],
            height=0.05,
            stretch=0.8,
            start=Angle.zero() + step,
            length=Angle.fullcircle() - step
        ),
        repeat=1
    )
