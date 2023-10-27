from pint import UnitRegistry

units = UnitRegistry()
units.define("beat = []")
units.define("bpm = beat / minute")
units.define("bps = beat / second")
units.define("steps_per_minute = 0.5 * rpm = spm")
units.define("pace = minutes / kilometers")
units.define("pace_km = minutes / kilometers = paceKm")
units.define("pace_mile = minutes / miles = paceM")
units.define("pace_kt = minutes / nautical_mile = paceKt")

units.define("number = []")
# this is a hack to support "lat" and "lon" as a metric.
units.define("location = []")


def metres(n):
    return units.Quantity(n, units.m)


if __name__ == "__main__":

    rpms = units.Quantity(10, "rpm")

    print(rpms.to("spm"))

    speed = units.Quantity('10 kph')
    pace = (1 / speed).to('pace')
    print(pace)

    print("{:D}".format(pace))