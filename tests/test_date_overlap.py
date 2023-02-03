import datetime

from gopro_overlay.date_overlap import DateRange


def test_date_overlap():
    r1 = DateRange(start=datetime.datetime(2012, 1, 15), end=datetime.datetime(2012, 5, 10))
    r2 = DateRange(start=datetime.datetime(2012, 3, 20), end=datetime.datetime(2012, 9, 15))

    overlap = r1.overlap_seconds(r2)

    assert overlap == 4406400


def test_date_overlap_doesnt():
    r1 = DateRange(start=datetime.datetime(2023, 2, 2, 19, 48, 9), end=datetime.datetime(2023, 2, 2, 19, 51, 30))
    r2 = DateRange(start=datetime.datetime(2023, 2, 2, 11, 40, 43), end=datetime.datetime(2023, 2, 2, 12, 16, 36))

    overlap = r1.overlap_seconds(r2)

    assert overlap == 0
