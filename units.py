
from pint import UnitRegistry

units = UnitRegistry()
units.define("beat = []")
units.define("bpm = beat / minute")
units.define("bps = beat / second")
units.define("rps = revolution / second")

