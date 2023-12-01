import pytest

from gopro_overlay.smoothing import SimpleExponential, Kalman
from gopro_overlay.units import units


def test_ses():
    ses = SimpleExponential(alpha=0.4)

    assert ses.update(3.0) == 3.0
    assert ses.update(5.0) == 3.0
    assert ses.update(9.0) == 3.8
    assert ses.update(20.0) == 5.88


# no idea really if this is a good implementation, but this will check at least if we
# break/change the current one by accident.
def test_kalman():
    kal = Kalman()

    assert kal.update(1.0) == 1.0
    assert kal.update(2.0) == 1.0909090909090908
    assert kal.update(3.0) == 1.3969465648854962
    assert kal.update(-1.0) == 0.9018776499091459


def test_kalman_units_and_nones():
    k = Kalman()

    assert k.update(None) == 0.0
    assert k.update(units.Quantity(1, "mps")).m == pytest.approx(0.0909, abs=0.001)
    assert k.update(units.Quantity(1, "mps")).m == pytest.approx(0.2366, abs=0.001)
    assert k.update(None).m == pytest.approx(0.1878, abs=0.001)
    assert k.update(units.Quantity(1, "mps")).m == pytest.approx(0.3783, abs=0.001)
