from gopro_overlay.smoothing import SimpleExponential, Kalman


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
