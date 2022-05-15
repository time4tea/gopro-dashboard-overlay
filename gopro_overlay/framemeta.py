import bisect

from gopro_overlay.ffmpeg import load_gpmd_from, MetaMeta
from gopro_overlay.gpmd import NewGPS5EntryConverter, DetermineTimestampOfFirstSHUTVisitor, GPSVisitor, GoproMeta, \
    CalculateCorrectionFactorsVisitor, CorrectionFactorsPacketTimeCalculator, CoriTimestampPacketTimeCalculator
from gopro_overlay.timeunits import Timeunit, timeunits


class View:
    def __init__(self, data, version):
        self.data = data
        self.version = version


class Window:

    def __init__(self, ts, duration: Timeunit, samples, key=lambda e: 1, fmt=lambda v: v, missing=None):
        self.ts = ts
        self.duration = duration
        self.samples = samples
        self.tick = (duration / samples).align(timeunits(millis=100))
        self.key = key
        self.fmt = fmt
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
                entry = self.cache.setdefault(current, self.ts.get(current))
                value = self.key(entry)
                if value is not None:
                    data.append(self.fmt(value))
                else:
                    data.append(self.missing)
            current += self.tick

        self.version += 1
        self.last_time = at
        self.last_view = View(data, self.version)

        return self.last_view


class Stepper:

    def __init__(self, framemeta, step: Timeunit):
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


class FrameMeta:
    def __init__(self):
        self.modified = False
        self.framelist = []
        self.frames = {}

    def __len__(self):
        self.check_modified()
        return len(self.framelist)

    def stepper(self, step: Timeunit):
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

    def get(self, frame_time: Timeunit, interpolate=True):
        self.check_modified()

        if frame_time in self.frames:
            return self.frames[frame_time]

        if not interpolate:
            raise KeyError(f"Frame at {frame_time}ms not found")

        return self._get_interpolate(frame_time)

    def _get_interpolate(self, frame_time):

        if frame_time < self.min:
            print(f"Request for data at time {frame_time}, before start of metadata, returning first item")
            return self.frames[self.framelist[0]]

        if frame_time > self.max:
            print(f"Request for data at time {frame_time}, after end of metadata, returning last item")
            return self.frames[self.framelist[-1]]

        later_idx = bisect.bisect_left(self.framelist, frame_time)
        earlier_idx = later_idx - 1

        later_time = self.framelist[later_idx]
        earlier_time = self.framelist[earlier_idx]

        later_item = self.frames[later_time]
        earlier_item = self.frames[earlier_time]

        pts_delta = later_time - earlier_time
        gps_delta = timeunits(seconds=(later_item.dt - earlier_item.dt).total_seconds())
        delta = (gps_delta * ((frame_time - earlier_time) / pts_delta))
        wanted_date = delta.timedelta() + earlier_item.dt

        return earlier_item.interpolate(other=later_item, dt=wanted_date)

    def items(self):
        self.check_modified()
        return [self.frames[k] for k in self.framelist]

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


def framemeta_from_meta(meta, units, metameta=None):
    frame_meta = FrameMeta()

    cori_timestamp = meta.accept(DetermineTimestampOfFirstSHUTVisitor()).timestamp

    if cori_timestamp is None:
        assert metameta is not None
        correction_factors = meta.accept(
            CalculateCorrectionFactorsVisitor("GPS5", metameta)
        ).factors()

        calculator = CorrectionFactorsPacketTimeCalculator(correction_factors)
    else:
        calculator = CoriTimestampPacketTimeCalculator(cori_timestamp)

    converter = NewGPS5EntryConverter(
        units,
        calculator=calculator,
        on_item=lambda c, e: frame_meta.add(c, e)
    )

    meta.accept(GPSVisitor(converter=converter.convert))

    return frame_meta


def parse_gopro(gpmd_from, units, metameta: MetaMeta):
    return framemeta_from_meta(GoproMeta.parse(gpmd_from), units, metameta=metameta)


def framemeta_from(filepath, units, metameta: MetaMeta):
    gpmd_from = load_gpmd_from(filepath)
    return parse_gopro(gpmd_from, units, metameta)


def framemeta_from_datafile(datapath, units, metameta: MetaMeta):
    with open(datapath, "rb") as data:
        return parse_gopro(data.read(), units, metameta)
