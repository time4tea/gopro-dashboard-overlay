import bisect
from typing import Callable

from gopro_overlay import timeseries_process
from gopro_overlay.ffmpeg import load_gpmd_from, MetaMeta
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.gpmd_calculate import timestamp_calculator_for_packet_type
from gopro_overlay.gpmd_visitors_gps import GPS5EntryConverter, GPSVisitor
from gopro_overlay.gpmd_visitors_xyz import XYZVisitor, XYZComponentConverter
from gopro_overlay.timeunits import Timeunit, timeunits


class View:
    def __init__(self, data, version):
        self.data = data
        self.version = version


class Window:

    def __init__(self, ts, duration: Timeunit, samples, key=lambda e: 1, missing=None):
        self.ts = ts
        self.duration = duration
        self.samples = samples
        self.tick = (duration / samples).align(timeunits(millis=100))
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
                entry = self.cache[current] if current in self.cache else self.cache.setdefault(current, self.ts.get(current))
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

    def duration(self):
        self.check_modified()
        return self.framelist[-1]


def gps_framemeta(meta: GoproMeta, units, metameta=None):
    frame_meta = FrameMeta()

    meta.accept(
        GPSVisitor(
            converter=GPS5EntryConverter(
                units,
                calculator=timestamp_calculator_for_packet_type(meta, metameta, "GPS5"),
                on_item=lambda c, e: frame_meta.add(c, e)
            ).convert
        )
    )

    return frame_meta


def accl_framemeta(meta, units, metameta=None):
    framemeta = FrameMeta()

    meta.accept(
        XYZVisitor(
            "ACCL",
            XYZComponentConverter(
                frame_calculator=timestamp_calculator_for_packet_type(meta, metameta, "ACCL"),
                units=units,
                on_item=lambda t, x: framemeta.add(t, x)
            ).convert
        )
    )

    kalman = timeseries_process.process_kalman_pp3("accl", lambda i: i.accl)
    framemeta.process(kalman)

    return framemeta


def merge_frame_meta(gps: FrameMeta, other: FrameMeta, update: Callable[[FrameMeta], dict]):
    for item in gps.items():
        frame_time = item.timestamp
        interpolated = other.get(timeunits(millis=frame_time.magnitude))
        item.update(**update(interpolated))


def parse_gopro(gpmd_from, units, metameta: MetaMeta):
    gopro_meta = GoproMeta.parse(gpmd_from)
    gps_frame_meta = gps_framemeta(gopro_meta, units, metameta=metameta)
    accl_frame_meta = accl_framemeta(gopro_meta, units, metameta=metameta)

    merge_frame_meta(gps_frame_meta, accl_frame_meta, lambda a: {"accl": a.accl})

    return gps_frame_meta


def framemeta_from(filepath, units, metameta: MetaMeta):
    gpmd_from = load_gpmd_from(filepath)
    return parse_gopro(gpmd_from, units, metameta)


def framemeta_from_datafile(datapath, units, metameta: MetaMeta):
    with open(datapath, "rb") as data:
        return parse_gopro(data.read(), units, metameta)
