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

    assert kal.update(1.0) == 0.0
    assert kal.update(2.0) == 0.18181818181818182
    assert kal.update(3.0) == 0.633587786259542
    assert kal.update(-1.0) == 0.2961841308298001
