import array
import bisect
import collections
import datetime
import itertools
import struct
import warnings
from enum import Enum

from .ffmpeg import load_gpmd_from
from .point import Point, Point3
from .timeseries import Timeseries, Entry

GPMDStruct = struct.Struct('>4sBBH')

GPS5 = collections.namedtuple("GPS5", "lat lon alt speed speed3d")
XYZ = collections.namedtuple('XYZ', "y x z")


class GPSFix(Enum):
    NO = 0
    UNKNOWN = 1
    LOCK_2D = 2
    LOCK_3D = 3


type_mappings = {'c': 'c',
                 'L': 'L',
                 's': 'h',
                 'S': 'H',
                 'f': 'f',
                 'U': 'c',
                 'l': 'l',
                 'B': 'B',
                 'J': 'Q'
                 }


def _interpret_string(item):
    return item.rawdata.decode('utf-8', errors='replace').strip('\0')


def _interpret_timestamp(item):
    return datetime.datetime.strptime(item.rawdata.decode('utf-8', errors='replace'), '%y%m%d%H%M%S.%f').replace(
        tzinfo=datetime.timezone.utc)


def _struct_mapping_for(item, repeat=None):
    repeat = item.repeat if repeat is None else repeat
    return struct.Struct('>' + type_mappings[item.type_char] * repeat)


def _interpret_atom(item):
    return _struct_mapping_for(item).unpack_from(item.rawdata)[0]


def _interpret_list(item):
    return _struct_mapping_for(item).unpack_from(item.rawdata)


def _interpret_gps5(item):
    return [
        GPS5._make(
            _struct_mapping_for(item, repeat=5).unpack_from(
                item.rawdata[r * 4 * 5:(r + 1) * 4 * 5]
            )
        )
        for r in range(item.repeat)
    ]


def _interpret_gps_precision(item):
    return _interpret_atom(item) / 100.0


def _interpret_xyz(item):
    return [
        XYZ._make(
            _struct_mapping_for(item, repeat=3).unpack_from(
                item.rawdata[r * 2 * 3:(r + 1) * 2 * 3]
            )
        )
        for r in range(item.repeat)
    ]


def _interpret_gps_lock(item):
    return GPSFix(_interpret_atom(item))


def _interpret_stream_marker(item):
    return "Stream Marker"


def _interpret_device_marker(item):
    return "Device Marker"


interpreters = {
    "ACCL": _interpret_xyz,
    "DEVC": _interpret_device_marker,
    "DVNM": _interpret_string,
    "GPS5": _interpret_gps5,
    "GPSF": _interpret_gps_lock,
    "GPSP": _interpret_gps_precision,
    "GPSU": _interpret_timestamp,
    "GYRO": _interpret_xyz,
    "MWET": _interpret_list,
    "SCAL": _interpret_list,
    "SIUN": _interpret_string,
    "STMP": _interpret_atom,
    "STNM": _interpret_string,
    "STRM": _interpret_stream_marker,
    "TSMP": _interpret_atom,
    "WNDM": _interpret_list,
}


class GPMDInterpreted:

    def __init__(self, fourcc, item, interpreted):
        self.fourcc = fourcc
        self.item = item
        self.interpreted = interpreted

    def __str__(self):
        return f"GPMDInterpreted: Understood={self.understood} Interpreted={self.interpreted} Item={self.item}"

    @property
    def understood(self):
        return self.interpreted is not None


class GPMDInterpreter:

    def __init__(self, items):
        self.items = items

    def interpret(self):
        for item in self.items():
            yield GPMDInterpreted(
                item.fourcc,
                item,
                interpreters[item.fourcc](item) if item.fourcc in interpreters else None
            )


class GPMDItem:

    def __init__(self, fourcc, type, repeat, padded_length, rawdata):
        self._rawdata = rawdata
        self._padded_length = padded_length
        self._type = type
        self._repeat = repeat
        self._fourcc = fourcc

    @property
    def repeat(self):
        return self._repeat

    @property
    def type_char(self):
        return chr(self._type) if self._type != 0 else None

    @property
    def rawdata(self):
        return self._rawdata

    @property
    def fourcc(self):
        return self._fourcc

    @property
    def size(self):
        return GPMDStruct.size + self._padded_length if self._type != 0 else GPMDStruct.size

    @staticmethod
    def from_array(data, offset):
        code, type, size, repeat = GPMDStruct.unpack_from(data, offset=offset)
        code = code.decode()
        type = int(type)
        length = size * repeat
        padded_length = GPMDItem.extend(length)

        if type != 0 and padded_length >= 0:
            fmt = '>' + str(padded_length) + 's'
            s = struct.Struct(fmt)
            rawdata, = s.unpack_from(data, offset=offset + 8)
        else:
            rawdata = None

        return GPMDItem(code, type, repeat, padded_length, rawdata)

    def __str__(self):
        if self.rawdata is None:
            rawdata = "null"
            rawdatas = "null"
        else:
            rawdata = ' '.join(format(x, '02x') for x in self.rawdata)
            rawdatas = self.rawdata[0:50]

        return f"GPMDItem: FourCC={self.fourcc} Type={self.type_char} Len={self.size} [{rawdata}] [{rawdatas}]"

    @staticmethod
    def extend(n, base=4):
        i = n
        while i % base != 0:
            i += 1
        return i


class GPMDParser:

    def __init__(self, data: array.array):
        self.data = data

    def items(self):
        offset = 0
        while offset < len(self.data):
            item = GPMDItem.from_array(self.data, offset)
            yield item
            offset += item.size


class PacketCounter:

    def __init__(self):
        self.packet = 0

    def accept(self, interpreted):
        if interpreted.fourcc == "DEVC":
            self.packet += 1


class SampleCounter:

    def __init__(self, stream):
        self.item = None
        self.stream = stream
        self._saved = None
        self._last_sample_count = None
        self._current_sample_count = 0

    def accept(self, interpreted):
        if interpreted.fourcc == "TSMP":
            self._saved = interpreted
        elif interpreted.fourcc == self.stream:
            sample_count = self._saved.interpreted
            if self._last_sample_count is None:
                self._current_sample_count = sample_count
            else:
                self._current_sample_count = sample_count - self._last_sample_count

            self._last_sample_count = sample_count

    def count(self):
        return self._current_sample_count


class StreamClock:
    def __init__(self, step=None):
        self.step = step if step else 1001
        self.clock = -self.step

    def accept(self, interpreted):
        if interpreted.fourcc == "DEVC":
            self.clock += self.step

    def at(self, index, hertz):
        return self.clock + (self.step * index * (1.0 / hertz))


class GPS5Scaler:

    def __init__(self, units, on_item, max_dop=5.0, on_drop=lambda x: None):
        self.reset()
        self._units = units
        self._samples = SampleCounter("GPS5")
        self._packet_counter = PacketCounter()
        self._clock = StreamClock()
        self._on_item = on_item
        self._on_drop = on_drop
        self._max_dop = max_dop

    def reset(self):
        self._scale = None
        self._dop = None
        self._fix = None
        self._basetime = None

    def report_drop(self, message):
        self._on_drop(f"Packet: {self._packet_counter.packet} GPS Time: {self._basetime} Discarding GPS Location, {message}")

    def accept(self, interpreted):

        item_type = interpreted.fourcc

        self._samples.accept(interpreted)
        self._clock.accept(interpreted)
        self._packet_counter.accept(interpreted)

        if item_type == "STRM":
            self.reset()
        elif item_type == "GPSU":
            self._basetime = interpreted.interpreted
        elif item_type == "GPSF":
            self._fix = interpreted.interpreted
        elif item_type == "GPSP":
            self._dop = interpreted.interpreted
        elif item_type == "SCAL":
            self._scale = interpreted.interpreted
        elif item_type == "GPS5":
            if self._basetime is None:
                self.report_drop(f"Unknown GPS time")
            elif self._fix is None:
                self.report_drop("Unknown GPS Fix status")
            elif self._fix in (GPSFix.NO, GPSFix.UNKNOWN):
                self.report_drop(f"GPS is not locked (Status = {self._fix})")
            elif self._dop is None:
                self.report_drop("Unknown GPS DOP/Accuracy")
            elif self._scale is None:
                self.report_drop("Unknown scale (metadata stream error?)")
            else:
                if self._dop > self._max_dop:
                    self.report_drop(f"DOP Out of Range. DOP {self._dop} > Max DOP {self._max_dop}")

                points = interpreted.interpreted
                hertz = self._samples.count()

                if len(points) != hertz:
                    # this will happen for first sample in when recording spans multiple files (for second file onwards)
                    pass

                for index, point in enumerate(points):
                    scaled = [float(x) / float(y) for x, y in zip(point._asdict().values(), self._scale)]
                    scaled_point = GPS5._make(scaled)
                    point_datetime = self._basetime + datetime.timedelta(seconds=(index * (1.0 / len(points))))
                    self._on_item(
                        Entry(point_datetime,
                              clock=self._clock.at(index, hertz),
                              point=Point(scaled_point.lat, scaled_point.lon),
                              speed=self._units.Quantity(scaled_point.speed, self._units.mps),
                              alt=self._units.Quantity(scaled_point.alt, self._units.m))
                    )


class XYZScaler:

    def __init__(self, units, stream_name, on_item):
        self._on_item = on_item
        self._units = units
        self._clock = StreamClock()
        self._stream_name = stream_name
        self._samples = SampleCounter(stream_name)
        self._reset()

    def _reset(self):
        self._scale = None

    def accept(self, interpreted):

        item_type = interpreted.fourcc

        self._samples.accept(interpreted)
        self._clock.accept(interpreted)

        if item_type == "STRM":
            self._reset()
        elif item_type == "SCAL":
            self._scale = interpreted.interpreted
        elif item_type == self._stream_name:
            points = interpreted.interpreted
            hertz = self._samples.count()

            if len(points) != hertz:
                warnings.warn("Bug? - Δsamples != samples")

            for index, point in enumerate(points):

                components = point._asdict().values()

                divisors = self._scale
                if len(divisors) == 1 and len(components) > 1:
                    divisors = itertools.repeat(divisors[0], len(components))

                scaled = [float(x) / float(y) for x, y in zip(components, divisors)]
                scaled_point = XYZ._make(scaled)

                items = {
                    "clock": self._clock.at(index, hertz),
                    self._stream_name.lower(): Point3(scaled_point.x, scaled_point.y, scaled_point.z)
                }

                self._on_item(items)


class StreamScalers:

    def __init__(self, *args):
        self.scalers = args

    def accept(self, interpreted):
        [s.accept(interpreted) for s in self.scalers]


def timeseries_from(filepath, units, unhandled=lambda x: None, on_drop=lambda reason: None):
    meta = GPMDInterpreter(GPMDParser(load_gpmd_from(filepath)).items).interpret()

    timeseries = Timeseries()
    gps_scaler = GPS5Scaler(units=units,
                            max_dop=6.0,
                            on_item=lambda entry: timeseries.add(entry),
                            on_drop=on_drop
                            )

    for item in meta:
        if item.understood:
            gps_scaler.accept(item)
        else:
            unhandled(item.item)

    return timeseries


class Clocked:

    # Things that don't have a GPS time associated with them, just a stream time.
    def __init__(self):
        self.items = {}
        self.clocks = None

    def add(self, item):
        self.clocks = None
        entry = self.items.setdefault(item["clock"], {})
        entry.update(item)

    def closest(self, clock):
        if self.clocks is None:
            self.clocks = sorted(list(self.items.keys()))
        return self.items[self.clocks[bisect.bisect_right(self.clocks, clock)]]
