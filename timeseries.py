import bisect
from datetime import timedelta

import units


def process_ses(new, key, alpha=0.4):
    forecast = []
    previous = [None]

    def ses(item):
        current = key(item)
        try:
            if forecast:
                predicted = alpha * previous[0] + (1 - alpha) * forecast[-1]
                forecast.append(predicted)
                return {new: predicted}
            else:
                forecast.append(current)
                return {new: current}
        finally:
            previous[0] = current

    return ses


class Timeseries:

    def __init__(self, entries=None):
        self.entries = {}
        self.dates = []
        if entries is not None:
            self.add(*entries)

    @property
    def min(self):
        return self.dates[0]

    @property
    def max(self):
        return self.dates[-1]

    @property
    def size(self):
        return len(self.dates)

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

    def clip_to(self, other):

        wanted = [e for e in self.items() if other.min <= e.dt <= other.max]

        if not wanted:
            return Timeseries()

        if other.min < wanted[0].dt:
            wanted.insert(0, self.get(other.min))

        if other.max > wanted[-1].dt:
            wanted.append(self.get(other.max))

        return Timeseries(entries=wanted)

    def process_deltas(self, processor):

        diffs = list(zip(self.dates, self.dates[1:]))

        for a, b in diffs:
            result = processor(self.entries[a], self.entries[b])
            self.entries[a].update(**result)

    def process(self, processor):
        for e in self.dates:
            self.entries[e].update(**processor(self.entries[e]))


def entry_wants(v):
    return isinstance(v, int) or isinstance(v, float) or isinstance(v, units.units.Quantity)


class Entry:

    def __init__(self, dt, **kwargs):
        self.dt = dt
        self.items = {k: v for k, v in dict(**kwargs).items() if entry_wants(v)}

    def update(self, **kwargs):
        self.items.update(**kwargs)

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
            try:
                end = other.items[key]
                diff = end - start
                interp = start + (position * diff)
            except KeyError:
                interp = None
            items[key] = interp

        return Entry(dt, **items)
