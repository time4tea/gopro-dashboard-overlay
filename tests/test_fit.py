import pytest

from gopro_overlay import fit
from gopro_overlay.units import units
from tests.test_gpx import file_path_of_test_asset


def test_converting_fit_without_power_to_timeseries():
    ts = fit.load_timeseries(file_path_of_test_asset("fit-file-no-power.fit", in_dir="fit"), units)

    assert len(ts) == 8600

    item = ts.items()[26]

    assert item.point.lat == pytest.approx(51.3397, abs=0.0001)
    assert item.point.lon == pytest.approx(-2.572136, abs=0.0001)
    assert item.alt.units == units.m
    assert item.alt.magnitude == pytest.approx(96.6, abs=0.1)
    assert item.hr == units.Quantity(72, units.bpm)
    assert item.atemp == units.Quantity(16, units.celsius)
    assert item.odo == units.Quantity(53.77, units.m)
    assert item.gpsfix == 3


def test_converting_fit_with_power_to_timeseries():
    ts = fit.load_timeseries(file_path_of_test_asset("fit-file-with-power.fit", in_dir="fit"), units)

    assert len(ts) == 2945

    item = ts.items()[26]

    assert item.power == units.Quantity(80, units.watt)
    assert item.odo == units.Quantity(114.96, units.m)
    assert item.gpsfix == 3