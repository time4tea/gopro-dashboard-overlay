import bisect
from datetime import timedelta


class Timeseries:

    def __init__(self):
        self.entries = {}
        self.dates = []

    def _update(self):
        self.dates = sorted(list(self.entries.keys()))

    def add(self, *entries):
        for e in entries:
            self.entries[e.dt] = e
        self._update()

    def get(self, dt):
        if not self.dates or dt < self.dates[0]:
            raise ValueError("Date is before start")
        if dt > self.dates[-1]:
            raise ValueError("Date is after end")
        if dt in self.entries:
            return self.entries[dt]
        else:
            greater_idx = bisect.bisect_left(self.dates, dt)
            lesser_idx = greater_idx - 1

            return self.entries[self.dates[lesser_idx]].interpolate(self.entries[self.dates[greater_idx]], dt)

    def items(self):
        return [self.entries[k] for k in self.dates]


def entry_wants(v):
    return isinstance(v, int) or isinstance(v, float)


class Entry:

    def __init__(self, dt, **kwargs):
        self.dt = dt
        self.items = {k: v for k, v in dict(**kwargs).items() if entry_wants(v)}

    def __getattr__(self, item):
        return self.items.get(item, None)

    def interpolate(self, other, dt):
        if self.dt == other.dt:
            raise ValueError("Cannot interpolate between equal points")
        if self.dt > other.dt:
            raise ValueError("Lower point must be first")
        if dt < self.dt:
            raise ValueError("Wanted point before lower")
        if dt > other.dt:
            raise ValueError("Wanted point after other")

        if dt == self.dt:
            return self
        elif dt == other.dt:
            return other

        range = (other.dt - self.dt) / timedelta(milliseconds=1)
        point = (dt - self.dt) / timedelta(milliseconds=1)

        position = point / range

        items = {}
        for key in self.items.keys():
            start = self.items[key]
            end = other.items[key]
            diff = end - start
            interp = start + (position * diff)
            items[key] = interp

        return Entry(dt, **items)
