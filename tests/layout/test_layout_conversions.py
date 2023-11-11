import pytest
from pint import UndefinedUnitError, DimensionalityError

from gopro_overlay.layout_xml import Converters, FloatRange
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


speed = units.Quantity(100, units.mps)
distance = units.Quantity(100, units.m)
altitude = units.Quantity(100, units.m)
temp = units.Quantity(100, units.kelvin)


def test_default_units_are_mph_miles_metres():
    converters = Converters()
    assert converters.converter("speed")(speed).m == pytest.approx(223.693629, abs=0.000001)
    assert converters.converter("speed")(speed).units == units.mph

    assert converters.converter("distance")(distance).m == pytest.approx(0.0621371, abs=0.000001)
    assert converters.converter("distance")(distance).units == units.miles

    assert converters.converter("altitude")(altitude).m == pytest.approx(100, abs=0.000001)
    assert converters.converter("altitude")(altitude).units == units.metres

    assert converters.converter("temp")(temp).m == pytest.approx(-173.15, abs=0.01)
    assert converters.converter("temp")(temp).units == units.degC


def test_overriding_default_units():
    converters = Converters(speed_unit="kph", distance_unit="km", altitude_unit="foot", temperature_unit="kelvin")

    assert converters.converter("speed")(speed).units == units.kph
    assert converters.converter("distance")(distance).units == units.km
    assert converters.converter("altitude")(altitude).units == units.feet
    assert converters.converter("temp")(temp).units == units.kelvin

    assert converters.converter("speed")(speed).m == pytest.approx(360, abs=0.1)
    assert converters.converter("distance")(distance).m == pytest.approx(0.1, abs=0.1)
    assert converters.converter("altitude")(altitude).m == pytest.approx(328.0839895, abs=0.000001)
    assert converters.converter("temp")(temp).m == pytest.approx(100, abs=0.01)


def test_various_speed_conversions_dont_blow_up():
    for i in "mph, mps, kph, kph, knot".split(","):
        Converters(speed_unit=i).converter("speed")(speed)


def test_illegal_speed_conversion_does_blow_up():
    for i in "unknown, whatever".split(","):
        with pytest.raises(UndefinedUnitError):
            Converters(speed_unit=i).converter("speed")(speed)


def test_invalid_speed_conversion_does_blow_up():
    for i in "radian, kilogram".split(","):
        with pytest.raises(DimensionalityError):
            Converters(speed_unit=i).converter("speed")(speed)


def test_various_altitude_conversions_dont_blow_up():
    for i in "foot, mile, metre, meter, parsec, angstrom".split(","):
        Converters(altitude_unit=i).converter("altitude")(altitude)


def test_various_distance_conversions_dont_blow_up():
    for i in "mile, km, foot, nmi, meter, metre, parsec".split(","):
        Converters(distance_unit=i).converter("distance")(distance)


def test_various_temperature_conversions_dont_blow_up():
    for i in "degC, degF, kelvin".split(","):
        Converters(temperature_unit=i).converter("temp")(temp)


def test_float_range():
    assert 0.9 in FloatRange(0.0, 1.0)
    assert 1.0 in FloatRange(0.0, 1.0)
    assert 0.0 in FloatRange(0.0, 1.0)
    assert -0.1 not in FloatRange(0.0, 1.0)
    assert 1.1 not in FloatRange(0.0, 1.0)


def test_float_range_looks_a_bit_like_a_range():
    assert FloatRange(0.0, 1.0).start == 0.0
    assert FloatRange(0.0, 1.0).stop == 1.0


def test_pace_conversions_defaults():
    speed = units.Quantity('10 kph')
    converters = Converters()
    assert converters.converter("pace")(speed).m == pytest.approx(9.656, abs=0.001)
    assert converters.converter("pace_mile")(speed).m == pytest.approx(9.656, abs=0.001)
    assert converters.converter("pace_km")(speed).m == 6.0
    assert converters.converter("pace_kt")(speed).m == pytest.approx(11.112, abs=0.001)


def test_pace_conversions_zero_or_none():
    converters = Converters()
    speed = units.Quantity('0 kph')
    assert converters.converter("pace")(speed) is None
    assert converters.converter("pace_mile")(speed) is None
    assert converters.converter("pace_km")(speed) is None
    assert converters.converter("pace_kt")(speed) is None


def test_pace_conversions_defaults_km():
    speed = units.Quantity('10 kph')
    converters = Converters(distance_unit="km")
    assert converters.converter("pace")(speed).m == 6.0
    assert converters.converter("pace_mile")(speed).m == pytest.approx(9.656, abs=0.001)
    assert converters.converter("pace_km")(speed).m == 6.0
    assert converters.converter("pace_kt")(speed).m == pytest.approx(11.112, abs=0.001)


def test_spm_conversions_defaults():
    converters = Converters()
    assert converters.converter("spm")(units.Quantity('5 rpm')) == units.Quantity(10, "spm")
    assert converters.converter("spm")(units.Quantity('5.5 rpm')) == units.Quantity(11, "spm")
