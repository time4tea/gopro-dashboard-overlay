import pytest

from gopro_overlay.layout_xml import Converters
from gopro_overlay.units import units

# in tests not really bothered about the outcome of the conversion, only that they are recognised by the converter
# and they run ... i think?

converters = Converters()

def test_power_conversions():
    start = units.Quantity(100, units.watt)

    [converters.converter(i)(start) for i in ["kW", "watt", "hp"]]


def test_speed_conversion():
    start = units.Quantity(100, units.mps)

    [converters.converter(i)(start) for i in ["mph", "MPH", "knots", "knot", "fps"]]


def test_power_conversion():
    start = units.Quantity(100, units.W)

    [converters.converter(i)(start) for i in ["W", "kW", "hp"]]


def test_distance_conversion():
    start = units.Quantity(100, units.m)

    [converters.converter(i)(start) for i in ["mile", "miles", "m", "metres", "km", "nmi", "foot", "yard", "hand", "angstrom", "parsec"]]

def test_default_units_are_mph_miles_metres():

    speed = units.Quantity(100, units.mps)
    distance = units.Quantity(100, units.m)
    altitude = units.Quantity(100, units.m)

    converters = Converters()
    assert converters.converter("speed")(speed).m == pytest.approx(223.693629, abs=0.000001)
    assert converters.converter("speed")(speed).units == units.mph

    assert converters.converter("distance")(distance).m == pytest.approx(0.0621371, abs=0.000001)
    assert converters.converter("distance")(distance).units == units.miles

    assert converters.converter("altitude")(altitude).m == pytest.approx(100, abs=0.000001)
    assert converters.converter("altitude")(altitude).units == units.metres

def test_overriding_default_units():

    speed = units.Quantity(100, units.mps)
    distance = units.Quantity(100, units.m)
    altitude = units.Quantity(100, units.m)

    converters = Converters(speed_unit="kph", distance_unit="km", altitude_unit="foot")

    assert converters.converter("speed")(speed).units == units.kph
    assert converters.converter("distance")(distance).units == units.km
    assert converters.converter("altitude")(altitude).units == units.feet

    assert converters.converter("speed")(speed).m == pytest.approx(360, abs=0.1)
    assert converters.converter("distance")(distance).m == pytest.approx(0.1, abs=0.1)
    assert converters.converter("altitude")(altitude).m == pytest.approx(328.0839895, abs=0.000001)


