import bisect
import datetime

from gopro_overlay.ffmpeg import load_gpmd_from
from gopro_overlay.gpmd import NewGPS5EntryConverter, DetermineTimestampOfFirstSHUTVisitor, GPSVisitor, GoproMeta


class Stepper:

    def __init__(self, framemeta, step: datetime.timedelta):
        self._framemeta = framemeta
        self._step = step

    def __len__(self):
        max_ms = self._framemeta.framelist[-1]
        duration = datetime.timedelta(milliseconds=max_ms)
        steps = int(duration / self._step) + 1
        return steps

    def steps(self):
        end = self._framemeta.framelist[-1]
        running = 0
        while running <= end:
            yield running
            running += int(self._step.microseconds / 1000)


class FrameMeta:
    def __init__(self):
        self.modified = False
        self.framelist = []
        self.frames = {}

    def __len__(self):
        self.check_modified()
        return len(self.framelist)

    def stepper(self, step):
        self.check_modified()
        return Stepper(self, step)

    def add(self, time_ms, entry):
        self.frames[time_ms] = entry
        self.modified = True

    @property
    def min(self):
        self.check_modified()
        return self.framelist[0]

    @property
    def max(self):
        self.check_modified()
        return self.framelist[-1]

    def _update(self):
        self.framelist = sorted(list(self.frames.keys()))
        self.modified = False

    def check_modified(self):
        if self.modified:
            self._update()

    def get(self, time_ms, interpolate=True):
        self.check_modified()

        if time_ms in self.frames:
            return self.frames[time_ms]

        if not interpolate:
            raise KeyError(f"Frame at {time_ms}ms not found")

        if time_ms < self.min:
            print(f"Request for data at time {time_ms}, before start of metadata, returning first item")
            return self.frames[self.framelist[0]]

        later_idx = bisect.bisect_left(self.framelist, time_ms)
        earlier_idx = later_idx - 1

        later_time = self.framelist[later_idx]
        earlier_time = self.framelist[earlier_idx]

        later_item = self.frames[later_time]
        earlier_item = self.frames[earlier_time]

        pts_delta = later_time - earlier_time
        wanted_date = ((((later_item.dt - earlier_item.dt) / pts_delta) * (
            (time_ms - earlier_time) / pts_delta))) + earlier_item.dt

        return earlier_item.interpolate(other=later_item, dt=wanted_date)

    def items(self):
        self.check_modified()
        return self.framelist

    def process_deltas(self, processor, skip=1):
        self.check_modified()
        diffs = list(zip(self.framelist, self.framelist[skip:]))

        for a, b in diffs:
            updates = processor(self.frames[a], self.frames[b], skip)
            if updates:
                self.frames[a].update(**updates)

    def process(self, processor):
        self.check_modified()
        for e in self.framelist:
            updates = processor(self.frames[e])
            if updates:
                self.frames[e].update(**updates)


def framemeta_from_meta(meta, units):
    frame_meta = FrameMeta()

    cori_timestamp = meta.accept(DetermineTimestampOfFirstSHUTVisitor()).timestamp

    converter = NewGPS5EntryConverter(
        units,
        cori_timestamp=cori_timestamp,
        on_item=lambda c, e: frame_meta.add(c, e)
    )

    meta.accept(GPSVisitor(converter=converter.convert))

    return frame_meta


def framemeta_from(filepath, units):
    return framemeta_from_meta(GoproMeta.parse(load_gpmd_from(filepath)), units)
