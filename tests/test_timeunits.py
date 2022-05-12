from gopro_overlay.timeunits import timeunits


def test_simple_timeunits():
    assert timeunits(seconds=1) == timeunits(seconds=1)
    assert timeunits(millis=1) == timeunits(millis=1)
    assert timeunits(micros=1) == timeunits(micros=1)


def test_conversions():
    assert timeunits(millis=1) == timeunits(micros=1000)
    assert timeunits(seconds=1) == timeunits(micros=1000000)
    assert timeunits(minutes=1) == timeunits(seconds=60)
    assert timeunits(hours=1) == timeunits(minutes=60)
    assert timeunits(days=1) == timeunits(hours=24)


def test_add():
    assert timeunits(seconds=1) + timeunits(millis=1) == timeunits(millis=1001)


def test_subtract():
    assert timeunits(seconds=1) - timeunits(millis=1) == timeunits(millis=999)


def test_multiply():
    assert timeunits(seconds=1) * 5 == timeunits(seconds=5)
    assert 5 * timeunits(seconds=1) == timeunits(seconds=5)


def test_divide():
    assert timeunits(millis=1000) / 10 == timeunits(millis=100)
    assert timeunits(seconds=1) / timeunits(millis=1) == 1000


def test_ignores_partial_us():
    assert timeunits(micros=1000.1) == timeunits(micros=1000)


def test_abs():
    assert abs(timeunits(seconds=-1)) == timeunits(seconds=1)


def test_comparison():
    assert timeunits(seconds=1) > timeunits(seconds=0)
    assert timeunits(seconds=1) >= timeunits(seconds=0)
    assert timeunits(seconds=0) < timeunits(seconds=1)
    assert timeunits(seconds=0) <= timeunits(seconds=1)
    assert timeunits(seconds=0) != timeunits(seconds=1)


def test_dict_keys():
    a = {
        timeunits(seconds=10): "hello",
        timeunits(seconds=1): "goodbye",
    }
    assert a[timeunits(seconds=10)] == "hello"
