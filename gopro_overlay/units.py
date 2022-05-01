from pint import UnitRegistry

units = UnitRegistry()
units.define("beat = []")
units.define("bpm = beat / minute")
units.define("bps = beat / second")
units.define("rps = revolution / second")

units.define("number = []")
# this is a hack to support "lat" and "lon" as a metric.
units.define("location = []")


def metres(n):
    return units.Quantity(n, units.m)
