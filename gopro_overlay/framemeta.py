import bisect
import datetime
from datetime import timedelta
from typing import Callable, List, MutableMapping

from gopro_overlay.entry import Entry
from gopro_overlay.log import log
from gopro_overlay.timeunits import Timeunit, timeunits


class View:
    def __init__(self, data, version):
        self.data = data
        self.version = version


def find_best_alignment(duration: Timeunit, samples: int):
    tick = duration / samples
    if tick < timeunits(millis=1):
        raise ValueError("Too many samples for that duration")
    tick_ms = tick.millis()
    align = list([a for a in [100, 50, 25, 10, 5, 1] if a <= tick_ms])[0]
    return timeunits(millis=align)


class Window:

    def __init__(self, ts, duration: Timeunit, samples, key=lambda e: 1, missing=None):
        self.ts = ts
        self.duration = duration
        self.samples = samples
        alignment = find_best_alignment(duration, samples)
        self.tick = (duration / samples).align(alignment)
        self.key = key
        self.missing = missing

        self.last_time = None
        self.last_view = None
        self.cache = {}
        self.version = 0

    def view(self, at: Timeunit):

        if self.last_time is not None and abs(at - self.last_time) < self.tick:
            return self.last_view

        return self._view_recalc(at)

    def _view_recalc(self, at: Timeunit):

        at = at.align(timeunits(millis=100))

        start = at - self.duration / 2
        end = at + self.duration / 2

        current = start

        data = []

        while current < end:
            if current < self.ts.min or current > self.ts.max:
                data.append(self.missing)
            else:
                entry = self.cache[current] if current in self.cache else self.cache.setdefault(current,
                                                                                                self.ts.get(current))
                value = self.key(entry)
                if value is not None:
                    data.append(value)
                else:
                    data.append(self.missing)
            current += self.tick

        self.version += 1
        self.last_time = at
        self.last_view = View(data, self.version)

        return self.last_view


class Stepper:

    def __init__(self, framemeta: 'FrameMeta', step: Timeunit):
        self._framemeta = framemeta
        self._step = step

    def __len__(self):
        max_ms = self._framemeta.framelist[-1]
        steps = int(max_ms / self._step) + 1
        return steps

    def steps(self):
        end = self._framemeta.framelist[-1]
        running = timeunits(millis=0)
        while running <= end:
            yield running
            running += self._step


max_distance = timeunits(seconds=6)


class FrameMeta:
    def __init__(self, packets_per_second=18):
        self.modified = False
        self.pps = packets_per_second
        self.framelist: List[Timeunit] = []
        self.frames: MutableMapping[Timeunit, Entry] = {}

    def __len__(self):
        self.check_modified()
        return len(self.framelist)

    def __getitem__(self, item):
        return self.frames[self.framelist[item]]

    def packets_per_second(self):
        return self.pps

    def stepper(self, step: Timeunit):
        self.check_modified()
        return Stepper(self, step)

    def add(self, at_time: Timeunit, entry):
        self.frames[at_time] = entry
        self.modified = True

    def clone(self) -> 'FrameMeta':
        fm = FrameMeta()
        [fm.add(t, e) for t, e in self.frames.items()]
        return fm

    def date_at(self, t: Timeunit) -> datetime.datetime:
        return self.get(t).dt

    @property
    def min(self) -> Timeunit:
        self.check_modified()
        return self.framelist[0]

    @property
    def max(self) -> Timeunit:
        self.check_modified()
        return self.framelist[-1]

    @property
    def mid(self):
        return self.min + ((self.max - self.min) / 2)

    def _update(self):
        self.framelist = sorted(list(self.frames.keys()))
        self.modified = False

    def check_modified(self):
        if self.modified:
            self._update()

    def get(self, frame_time: Timeunit, interpolate=True) -> Entry:
        self.check_modified()

        if frame_time in self.frames:
            return self.frames[frame_time]

        if not interpolate:
            raise KeyError(f"Frame at {frame_time}ms not found")

        return self._get_interpolate(frame_time)

    def _get_interpolate(self, frame_time) -> Entry:

        if frame_time < self.min:
            log(f"Request for data at time {frame_time}, before start of metadata, returning first item")
            return self.frames[self.framelist[0]]

        if frame_time > self.max:
            log(f"Request for data at time {frame_time}, after end of metadata, returning last item")
            return self.frames[self.framelist[-1]]

        later_idx = bisect.bisect_left(self.framelist, frame_time)
        earlier_idx = later_idx - 1

        earlier_time = self.framelist[earlier_idx]
        earlier_item = self.frames[earlier_time]

        delta = frame_time - earlier_time

        if delta > max_distance:
            log(f"Closest item to wanted time {frame_time} is {delta} away")

        return earlier_item

    def items(self, step: timedelta = timedelta(seconds=0)):
        self.check_modified()

        last_dt = datetime.datetime(year=1900, month=1, day=1, tzinfo=datetime.timezone.utc)

        for pts in self.framelist:
            entry = self.frames[pts]
            entry_dt = entry.dt

            if entry_dt >= last_dt + step:
                last_dt = entry_dt

                yield entry

    def process_deltas(self, processor, skip=1, filter_fn: Callable[[Entry], bool] = lambda e: True):
        self.check_modified()
        diffs = list(zip(self.framelist, self.framelist[skip:]))

        for a, b in diffs:
            entry_a = self.frames[a]
            entry_b = self.frames[b]
            if filter_fn(entry_a) and filter_fn(entry_b):
                updates = processor(entry_a, entry_b, skip)
                if updates:
                    entry_a.update(**updates)

    def process(self, processor, filter_fn: Callable[[Entry], bool] = lambda e: True):
        self.check_modified()
        for pts in self.framelist:
            entry = self.frames[pts]
            if filter_fn(entry):
                updates = processor(entry)
                if updates:
                    entry.update(**updates)

    def duration(self):
        self.check_modified()
        return self.framelist[-1]


