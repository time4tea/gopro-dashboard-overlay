from gopro_overlay.timing import PoorTimer


def test_timer_times_something():
    timer = PoorTimer("my name")
    timer.time(lambda: 1 * 2)

    assert timer.count == 1
    assert timer.total > 0.0
    assert timer.name == "my name"
    assert timer.avg > 0.0
    assert len(str(timer))


def test_timer_works_even_if_its_not_called():
    timer = PoorTimer("other name")
    assert timer.count == 0
    assert timer.total == 0.0
    assert timer.name == "other name"
    assert timer.avg == 0.0
    assert len(str(timer))
