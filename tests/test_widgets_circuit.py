import random
from datetime import timedelta

from gopro_overlay import fake
from gopro_overlay.dimensions import Dimension
from gopro_overlay.privacy import NoPrivacyZone
from gopro_overlay.widgets.cairo import circuit
from gopro_overlay.widgets.cairo.cairo import CairoWidget
from gopro_overlay.widgets.cairo.circuit import CairoCircuit, Line
from gopro_overlay.widgets.map import Circuit
from tests.approval import approve_image
from tests.test_widgets import time_rendering

rng = random.Random()
rng.seed(12345)

ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)


def cairo_widget_test(widgets, rotation=0, repeat=1):
    return time_rendering(
        name="test_gauge",
        dimensions=Dimension(500, 500),
        widgets=[
            CairoWidget(size=Dimension(500, 500), rotation=rotation, widgets=widgets)
        ],
        repeat=repeat
    )


def pt():
    return ts.get(ts.min).point


@approve_image
def test_cairo_circuit_defaults():
    return cairo_widget_test([CairoCircuit(framemeta=ts, location=pt)])


@approve_image
def test_cairo_circuit_defaults_rotate():
    return cairo_widget_test([CairoCircuit(framemeta=ts, location=pt)], rotation=45)


@approve_image
def test_cairo_circuit_line_width():
    return cairo_widget_test(
        [CairoCircuit(framemeta=ts, location=pt, line=Line(circuit.black, circuit.white, width=0.05))])


@approve_image
def test_cairo_circuit_fill():
    return cairo_widget_test(
        [CairoCircuit(framemeta=ts, location=pt, line=Line((255, 0, 255), circuit.white, width=0.01))])


@approve_image
def test_cairo_circuit_outline():
    return cairo_widget_test(
        [CairoCircuit(framemeta=ts, location=pt, line=Line(circuit.black, (255, 0, 255), width=0.01))])


@approve_image
def test_cairo_circuit_location():
    return cairo_widget_test(
        [CairoCircuit(framemeta=ts, location=pt, loc=Line(circuit.blue, circuit.white, width=0.025))])


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
