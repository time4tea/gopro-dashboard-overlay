import datetime
from typing import Any


class TimeSeriesEntry:

    def __init__(self):
        self._data = {}

    def set(self, key, value):
        if key not in self._data:
            self._data[key] = value

    def get(self, key):
        return self._data.get(key, None)


class Timeseries:

    def __init__(self, resolution=1.0):
        self._resolution = resolution
        self._data = {}
        self._min = 1e50
        self._max = -1e50

    @property
    def size(self):
        return len(self._data)

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def resolution(self):
        return self._resolution

    def _round(self, ts: datetime.datetime) -> float:
        stamp = ts.timestamp()
        return round(stamp * (1.0 / self._resolution)) / (1.0 / self._resolution)

    def update(self, ts: datetime.datetime, key: str, value: Any):
        rounded = self._round(ts)
        entry = self._data.setdefault(rounded, TimeSeriesEntry())
        self._min = min(self._min, rounded)
        self._max = max(self._max, rounded)
        entry.set(key, value)

    def get(self, ts, key):
        rounded = self._round(ts)
        if rounded < self.min or rounded > self.max:
            raise Exception("time out of bounds")
        return self._data.get(rounded, TimeSeriesEntry()).get(key)
