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
