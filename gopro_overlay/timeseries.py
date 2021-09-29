import bisect
import datetime
from datetime import timedelta

from .point import Point
from .units import units


def entry_wants(v):
    return isinstance(v, int) or isinstance(v, float) or isinstance(v, units.Quantity) or isinstance(v, Point)


class Entry:

    def __init__(self, dt, **kwargs):
        self.dt = dt
        self.items = {k: v for k, v in dict(**kwargs).items() if entry_wants(v)}

    def update(self, **kwargs):
        self.items.update(**kwargs)

    def __getattr__(self, item):
        return self.items.get(item, None)

    def __str__(self):
        return f"Entry: {self.dt} - {self.items}"

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
                interp = start + (diff * position)
            except KeyError:
                interp = None
            items[key] = interp

        return Entry(dt, **items)


class Timeseries:

    def __init__(self, entries=None):
        self.entries = {}
        self.dates = []
        if entries is not None:
            self.add(*entries)

    @property
    def min(self) -> datetime.datetime:
        return self.dates[0]

    @property
    def max(self) -> datetime.datetime:
        return self.dates[-1]

    def __len__(self):
        return len(self.dates)

    def _update(self):
        self.dates = sorted(list(self.entries.keys()))

    def add(self, *entries: Entry):
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

    def clip_to_datetimes(self, dt_min, dt_max):

        index_min = bisect.bisect_left(self.dates, dt_min)
        index_max = bisect.bisect_right(self.dates, dt_max)

        if self.dates[index_min] > dt_min and index_min > 0:
            index_min = index_min - 1

        if self.dates[index_max] < dt_max and index_max < len(self.dates) - 1:
            index_max = index_max + 1

        dates = self.dates[index_min:index_max + 1]

        wanted = [self.entries[d] for d in dates]

        if not wanted:
            return Timeseries()

        return Timeseries(entries=wanted)

    def clip_to(self, other):
        return self.clip_to_datetimes(other.min, other.max)

    def backfill(self, delta):
        to_add = []
        current = self.min
        while current <= self.max:
            if current not in self.entries:
                to_add.append(self.get(current))
            current += delta
        if to_add:
            self.add(*to_add)
        return len(to_add)

    def process_deltas(self, processor, skip=1):

        diffs = list(zip(self.dates, self.dates[skip:]))

        for a, b in diffs:
            updates = processor(self.entries[a], self.entries[b], skip)
            if updates:
                self.entries[a].update(**updates)

    def process(self, processor):
        for e in self.dates:
            updates = processor(self.entries[e])
            if updates:
                self.entries[e].update(**updates)


class Window:

    def __init__(self, ts, duration, samples, key=lambda e: e.alt, missing=None):
        self.ts = ts
        self.duration = duration
        self.samples = samples
        self.tick = duration / samples
        self.key = key
        self.missing = missing

        self.last_time = None
        self.last_view = None

    def view(self, at):

        if self.last_time is not None and abs(at - self.last_time) < self.tick:
            return self.last_view

        start = at - self.duration / 2
        end = at + self.duration / 2

        current = start

        data = []

        while current < end:
            if current < self.ts.min or current > self.ts.max:
                data.append(self.missing)
            else:
                data.append(self.key(self.ts.get(current)))
            current += self.tick

        self.last_time = at
        self.last_view = data

        return data

