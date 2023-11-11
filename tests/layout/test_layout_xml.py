import datetime

from gopro_overlay.layout_components import metric_value
from gopro_overlay.layout_xml import metric_accessor_from, date_formatter_from, Converters, quantity_formatter_for
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


def test_metric_none_after_conversion():
    speed = units.Quantity(0, units.mph)

    converters = Converters()

    entry = Entry(datetime_of(1), speed=speed)

    some_default_value = 123

    value = metric_value(
        lambda: entry,
        accessor=metric_accessor_from("speed"),
        converter=converters.converter("pace"),
        formatter=lambda q: q.m,
        default=some_default_value
    )

    assert value() == some_default_value


def test_formatting():
    assert (quantity_formatter_for("pace", None)((1 / units.Quantity("60 mph")).to("pace_miles"))) == "1:00"
    assert (quantity_formatter_for("pace", None)((1 / units.Quantity("30 mph")).to("pace_miles"))) == "2:00"


def test_date_formatter():
    entry = lambda: Entry(datetime_of(1644606742))

    utc = datetime.timezone.utc
    # timezone doesn't really want to be called externally..., and don't want to depend on pytz
    sort_of_pst = datetime.timezone.__new__(datetime.timezone, datetime.timedelta(hours=-8), "Bodge/PST")

    # Will just have to accept that calling with tz=None will do local tz, as its cached in datetime.py
    assert date_formatter_from(entry, "%Y/%m/%d %H:%M:%S.%f", tz=utc)() == "2022/02/11 19:12:22.000000"
    assert date_formatter_from(entry, "%Y/%m/%d %H:%M:%S.%f", tz=sort_of_pst)() == "2022/02/11 11:12:22.000000"
