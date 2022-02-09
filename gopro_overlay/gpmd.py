import array
import collections
import datetime
import itertools
import struct
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
    "TMPC": _interpret_atom,
    "STNM": _interpret_string,
    "STRM": _interpret_stream_marker,
    "TSMP": _interpret_atom,
    "WNDM": _interpret_list,
}


class GPMDContainer:

    def __init__(self, fourcc, size, repeat, padded_length, items):
        self.fourcc = fourcc
        self.items = items
        self._size = size
        self._repeat = repeat
        self._padded_length = padded_length

    def __str__(self) -> str:
        return f"GPMDContainer: {self.fourcc} " \
               f"Items: {len(self.items)} " \
               f"Size: {self._size} " \
               f"Repeat: {self._repeat} " \
               f"Length: {self._padded_length} " \
               f"Item Types {[i.fourcc for i in self.items]}"

    @property
    def size(self):
        return GPMDStruct.size + self._padded_length

    @property
    def is_container(self):
        return True

    def accept(self, visitor):

        method = f"vic_{self.fourcc}"
        if hasattr(visitor, method):
            container_visitor = getattr(visitor, method)(self, set([i.fourcc for i in self.items]))

            if container_visitor is not None:
                for i in self.items:
                    i.accept(container_visitor)

                container_visitor.v_end()


class GPMDItem:

    def __init__(self, fourcc, type_char_code, repeat, padded_length, rawdata):
        self._rawdata = rawdata
        self._padded_length = padded_length
        self._type = chr(type_char_code)
        self._repeat = repeat
        self._fourcc = fourcc

    @property
    def repeat(self):
        return self._repeat

    @property
    def type_char(self):
        return self._type

    @property
    def rawdata(self):
        return self._rawdata

    @property
    def fourcc(self):
        return self._fourcc

    @property
    def size(self):
        return GPMDStruct.size + self._padded_length if self._type != 0 else GPMDStruct.size

    def accept(self, visitor):
        method = f"vi_{self.fourcc}"
        if hasattr(visitor, method):
            getattr(visitor, method)(self)

    def __str__(self):
        if self.rawdata is None:
            rawdata = "null"
            rawdatas = "null"
        else:
            rawdata = ' '.join(format(x, '02x') for x in self.rawdata)
            rawdatas = self.rawdata[0:50]

        return f"GPMDItem: {self.fourcc} " \
               f"Type={self.type_char} " \
               f"Repeat: {self._repeat} " \
               f"Len={self.size}/{self._padded_length}" \
               f" [{rawdata}] [{rawdatas}]"


class GPMDParser:

    def __init__(self, data: array.array):
        self.data = data

    def items(self):
        offset = 0
        while offset < len(self.data):
            item = self.from_array(self.data, offset)
            yield item
            offset += item.size

    def from_array(self, data, offset):
        fourcc, type_char_code, size, repeat = GPMDStruct.unpack_from(data, offset=offset)
        fourcc = fourcc.decode()
        length = size * repeat
        padded_length = GPMDParser.extend(length)

        if type_char_code != 0 and padded_length >= 0:
            fmt = '>' + str(padded_length) + 's'
            s = struct.Struct(fmt)
            rawdata, = s.unpack_from(data, offset=offset + 8)

            return GPMDItem(fourcc, type_char_code, repeat, padded_length, rawdata)
        else:
            offset += GPMDStruct.size
            child_data = data[offset:padded_length + offset]

            children = []

            bob_offset = 0

            while bob_offset < len(child_data):
                child = self.from_array(child_data, bob_offset)
                children.append(child)
                bob_offset += child.size

            return GPMDContainer(fourcc, size, repeat, padded_length, children)

    @staticmethod
    def extend(n, base=4):
        i = n
        while i % base != 0:
            i += 1
        return i


def interpret_item(item):
    return interpreters[item.fourcc](item)


class XYZStreamVisitor:

    def __init__(self, on_item):
        self._on_item = on_item

    def vi_STMP(self, item):
        self._timestamp = interpret_item(item)

    def vi_TSMP(self, item):
        self._total_samples = interpret_item(item)

    def vi_ORIN(self, item):
        pass

    def vi_SCAL(self, item):
        self._scale = interpret_item(item)

    def vi_TMPC(self, item):
        self._temperature = interpret_item(item)

    def vi_ACCL(self, item):
        self._type = item.fourcc
        self._points = interpret_item(item)

    def vi_GYRO(self, item):
        self._type = item.fourcc
        self._points = interpret_item(item)

    def v_end(self):
        for index, point in enumerate(self._points):

            components = point._asdict().values()

            divisors = self._scale
            if len(divisors) == 1 and len(components) > 1:
                divisors = itertools.repeat(divisors[0], len(components))

            scaled = [float(x) / float(y) for x, y in zip(components, divisors)]
            scaled_point = XYZ._make(scaled)

            items = {
                self._type.lower(): Point3(scaled_point.x, scaled_point.y, scaled_point.z)
            }

            self._on_item(items)


class GPS5StreamVisitor:

    def __init__(self, counter, units, max_dop, on_item, on_drop):
        self._max_dop = max_dop
        self._counter = counter
        self._units = units
        self._on_item = on_item
        self._on_drop = on_drop

        self._samples = None
        self._basetime = None
        self._fix = None
        self._scale = None
        self._drop = None
        self._points = None

    def vi_TSMP(self, item):
        self._samples = interpret_item(item)

    def vi_GPSU(self, item):
        self._basetime = interpret_item(item)

    def vi_GPSF(self, item):
        self._fix = interpret_item(item)

    def vi_GPSP(self, item):
        self._dop = interpret_item(item)

    def vi_SCAL(self, item):
        self._scale = interpret_item(item)

    def vi_GPS5(self, item):
        self._points = interpret_item(item)

    def report_drop(self, message):
        self._on_drop(f"Packet: {self._counter} GPS Time: {self._basetime} Discarding GPS Location, {message}")

    def v_end(self):
        if self._dop > self._max_dop:
            self.report_drop(f"DOP Out of Range. DOP {self._dop} > Max DOP {self._max_dop}")
        elif self._fix in (GPSFix.NO, GPSFix.UNKNOWN):
            self.report_drop(f"GPS is not locked (Status = {self._fix})")
        elif self._dop is None:
            self.report_drop("Unknown GPS DOP/Accuracy")
        elif self._scale is None:
            self.report_drop("Unknown scale (metadata stream error?)")
        else:
            for index, point in enumerate(self._points):
                scaled = [float(x) / float(y) for x, y in zip(point._asdict().values(), self._scale)]
                scaled_point = GPS5._make(scaled)
                point_datetime = self._basetime + datetime.timedelta(seconds=(index * (1.0 / len(self._points))))
                self._on_item(
                    Entry(point_datetime,
                          dop=self._units.Quantity(self._dop, self._units.location),
                          packet=self._units.Quantity(self._counter, self._units.location),
                          packet_index=self._units.Quantity(index, self._units.location),
                          point=Point(scaled_point.lat, scaled_point.lon),
                          speed=self._units.Quantity(scaled_point.speed, self._units.mps),
                          alt=self._units.Quantity(scaled_point.alt, self._units.m))
                )


class GPSVisitor:

    def __init__(self, units, max_dop, on_item, on_drop):
        self.on_drop = on_drop
        self.on_item = on_item
        self.max_dop = max_dop
        self.units = units
        self._counter = 0

    def vic_DEVC(self, item, contents):
        self._counter += 1
        return self

    def vic_STRM(self, item, contents):
        if "GPS5" in contents:
            return GPS5StreamVisitor(self._counter, units=self.units, max_dop=self.max_dop, on_item=self.on_item,
                                     on_drop=self.on_drop)

    def v_end(self):
        pass


def timeseries_from_data(data, units, unhandled=lambda x: None, on_drop=lambda reason: None):
    ts = Timeseries()

    visitor = GPSVisitor(units=units, max_dop=6.0, on_item=lambda e: ts.add(e), on_drop=on_drop)

    for i in GPMDParser(data).items():
        i.accept(visitor)

    return ts


def timeseries_from(filepath, **kwargs):
    return timeseries_from_data(load_gpmd_from(filepath), **kwargs)
