import pytest

from gopro_overlay.dimensions import Dimension
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.widgets.cairo import circuit
from gopro_overlay.widgets.cairo.cairo import CairoAdapter, CairoWidget
from gopro_overlay.widgets.cairo.circuit import CairoCircuit, Line
from gopro_overlay.widgets.map import Circuit
from tests.widgets import test_widgets_setup
from tests.approval import approve_image
from tests.widgets.test_widgets import time_rendering

ts = test_widgets_setup.ts


def cairo_widget_test(widget: CairoWidget, rotation=0, repeat=1):
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            CairoAdapter(size=Dimension(500, 500), rotation=rotation, widget=widget)
        ],
        repeat=repeat
    )


def pt():
    return ts.get(ts.min).point


@pytest.mark.gfx
@approve_image
def test_cairo_circuit_defaults():
    return cairo_widget_test(CairoCircuit(framemeta=ts, location=pt))


@pytest.mark.gfx
@approve_image
def test_cairo_circuit_defaults_rotate():
    return cairo_widget_test(CairoCircuit(framemeta=ts, location=pt), rotation=45)


@pytest.mark.gfx
@approve_image
def test_cairo_circuit_line_width():
    return cairo_widget_test(
        CairoCircuit(framemeta=ts, location=pt, line=Line(circuit.black, circuit.white, width=0.05))
    )


@pytest.mark.gfx
@approve_image
def test_cairo_circuit_fill():
    return cairo_widget_test(
        CairoCircuit(framemeta=ts, location=pt, line=Line((255, 0, 255), circuit.white, width=0.01))
    )


@pytest.mark.gfx
@approve_image
def test_cairo_circuit_outline():
    return cairo_widget_test(
        CairoCircuit(framemeta=ts, location=pt, line=Line(circuit.black, (255, 0, 255), width=0.01))
    )


@pytest.mark.gfx
@approve_image
def test_cairo_circuit_location():
    return cairo_widget_test(
        CairoCircuit(framemeta=ts, location=pt, loc=Line(circuit.blue, circuit.white, width=0.025))
    )


@pytest.mark.gfx
@approve_image
def test_circuit():
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            Circuit(
                dimensions=Dimension(500, 500),
                framemeta=ts,
                privacy_zone=NoPrivacyZone(),
                location=lambda: ts.get(ts.min).point,
            )
        ],
        repeat=100
    )
