from gopro_overlay.layout_xml import metric_accessor_from
from gopro_overlay.timeseries import Entry
from gopro_overlay.units import units
from tests.test_timeseries import datetime_of


def test_metric_accessor_speed():
    speed = units.Quantity(10, units.mph)
    cspeed = units.Quantity(20, units.mph)
    entry = Entry(datetime_of(0), speed=speed, cspeed=cspeed)

    assert metric_accessor_from("speed")(entry) == speed
    assert metric_accessor_from("cspeed")(entry) == cspeed


def test_metric_accessor_speed_fallback():
    cspeed = units.Quantity(20, units.mph)
    entry = Entry(datetime_of(0), cspeed=cspeed)

    assert metric_accessor_from("speed")(entry) == cspeed
