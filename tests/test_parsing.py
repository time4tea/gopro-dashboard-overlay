import datetime

from gopro_overlay.parsing import parse_time


def test_parsing_time_seconds():
    assert parse_time("3").time() == datetime.time(second=3)
    assert parse_time("3.25").time() == datetime.time(second=3, microsecond=250000)
    assert parse_time("30.25").time() == datetime.time(second=30, microsecond=250000)


def test_parsing_time_minutes():
    assert parse_time("1:3").time() == datetime.time(minute=1, second=3)
    assert parse_time("13:3.25").time() == datetime.time(minute=13, second=3, microsecond=250000)


def test_parsing_time_hours():
    assert parse_time("1:1:3").time() == datetime.time(hour=1, minute=1, second=3)
    assert parse_time("5:13:3.25").time() == datetime.time(hour=5, minute=13, second=3, microsecond=250000)
