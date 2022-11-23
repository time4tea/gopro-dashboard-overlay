import array
import collections
import datetime
import itertools
import struct
from enum import Enum
from typing import List

from .timeunits import timeunits

GPMDStruct = struct.Struct('>4sBBH')

GPS5 = collections.namedtuple("GPS5", "lat lon alt speed speed3d")
XYZ = collections.namedtuple('XYZ', "x y z")
VECTOR = collections.namedtuple("VECTOR", "a b c")
QUATERNION = collections.namedtuple("QUATERNION", "w x y z")


class GPSFix(Enum):
    NO = 0
    UNKNOWN = 1
    LOCK_2D = 2
    LOCK_3D = 3


GPS_FIXED = {GPSFix.LOCK_3D, GPSFix.LOCK_2D}
GPS_FIXED_VALUES = {GPSFix.LOCK_3D.value, GPSFix.LOCK_2D.value}

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


def _interpret_string(item, *args):
    return str(item.rawdata, encoding='unicode_escape', errors="replace").strip('\0')


def _interpret_gps_timestamp(item, *args):
    return datetime.datetime.strptime(
        item.rawdata.decode(
            'utf-8',
            errors='replace'
        ),
        '%y%m%d%H%M%S.%f').replace(tzinfo=datetime.timezone.utc)


def _struct_mapping_for(item, repeat=None):
    repeat = item.repeat if repeat is None else repeat
    return struct.Struct('>' + type_mappings[item.type_char] * repeat)


def _interpret_atom(item, *args):
    return _struct_mapping_for(item).unpack_from(item.rawdata)[0]


def _interpret_timestamp(item, *args):
    return timeunits(micros=_interpret_atom(item, *args))


def _interpret_list(item, *args):
    return _struct_mapping_for(item).unpack_from(item.rawdata)


def _interpret_element(item, scale):
    single = _struct_mapping_for(item, repeat=1)
    mapping = _struct_mapping_for(item, repeat=item.size // single.size)

    if item.size > 1 and len(scale) == 1:
        scale = list(itertools.repeat(scale[0], item.size))

    def unpack_single(r):
        unscaled = mapping.unpack_from(item.rawdata[r * item.size: (r + 1) * item.size])
        return [float(x) / float(y) for x, y in zip(unscaled, scale)]

    return [unpack_single(r) for r in range(item.repeat)]


def _interpret_gps5(item, scale) -> List[GPS5]:
    return [GPS5._make(it) for it in _interpret_element(item, scale)]


def _interpret_gps_precision(item, *args) -> float:
    return _interpret_atom(item) / 100.0


def _interpret_xyz(item, scale) -> List[XYZ]:
    return [XYZ._make(it) for it in _interpret_element(item, scale)]


def _interpret_vector(item, scale) -> List[VECTOR]:
    return [VECTOR._make(it) for it in _interpret_element(item, scale)]


def _interpret_quaternion(item, scale) -> List[QUATERNION]:
    return [QUATERNION._make(it) for it in _interpret_element(item, scale)]


def _interpret_gps_lock(item, *args) -> GPSFix:
    return GPSFix(_interpret_atom(item))


def _interpret_stream_marker(item, *args) -> str:
    return "Stream Marker"


def _interpret_device_marker(item, *args):
    return "Device Marker"


interpreters = {
    "ACCL": _interpret_xyz,
    "CORI": _interpret_quaternion,
    "DEVC": _interpret_device_marker,
    "DVNM": _interpret_string,
    "GPS5": _interpret_gps5,
    "GPSF": _interpret_gps_lock,
    "GPSP": _interpret_gps_precision,
    "GPSU": _interpret_gps_timestamp,
    "GRAV": _interpret_vector,
    "GYRO": _interpret_xyz,
    "MWET": _interpret_list,
    "ORIN": _interpret_string,
    "SCAL": _interpret_list,
    "SIUN": _interpret_string,
    "STMP": _interpret_timestamp,
    "STNM": _interpret_string,
    "STRM": _interpret_stream_marker,
    "TICK": _interpret_atom,
    "TMPC": _interpret_atom,
    "TOCK": _interpret_atom,
    "TSMP": _interpret_atom,
    "WNDM": _interpret_list,
}


def interpret_item(item, scale=None):
    try:
        return interpreters[item.fourcc](item, scale)
    except KeyError:
        raise KeyError(f"No interpreter is configured for packets of type {item.fourcc}") from None


class GPMDContainer:

    def __init__(self, fourcc, size, repeat, padded_length, items):
        self.fourcc = fourcc
        self.items = items
        self._size = size
        self._repeat = repeat
        self._padded_length = padded_length

    def __str__(self) -> str:
        return f"GPMDContainer: {self.fourcc}" \
               f", #Items: {len(self)}" \
               f", Size(Bytes): {self._size}" \
               f", Repeat: {self._repeat}" \
               f", Length(Bytes): {self._padded_length}" \
               f", Item Types {[i.fourcc for i in self.items]}"

    def __len__(self):
        return len(self.items)

    @property
    def bytecount(self):
        return GPMDStruct.size + self._padded_length

    @property
    def itemset(self):
        return set([i.fourcc for i in self.items])

    def with_type(self, fourcc):
        return [i for i in self.items if i.fourcc == fourcc]

    def accept(self, visitor):

        method = f"vic_{self.fourcc}"
        if hasattr(visitor, method):
            container_visitor = getattr(visitor, method)(self, self.itemset)

            if container_visitor is not None:
                for i in self.items:
                    i.accept(container_visitor)

                container_visitor.v_end()


class GPMDItem:

    def __init__(self, fourcc, type_char_code, size, repeat, padded_length, rawdata):
        self._fourcc = fourcc
        self._type = chr(type_char_code)
        self._size = size
        self._repeat = repeat
        self._padded_length = padded_length
        self._rawdata = rawdata

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
        return self._size

    @property
    def bytecount(self):
        return GPMDStruct.size + self._padded_length if self._type != 0 else GPMDStruct.size

    def interpret(self, scale=None):
        return interpret_item(self, scale)

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

        return f"GPMDItem: {self.fourcc}" \
               f", Type={self.type_char}" \
               f", Size={self.size}" \
               f", Repeat: {self._repeat}" \
               f", Length Bytes={self.bytecount}/{self._padded_length}" \
               f" [{rawdata}] [{rawdatas}]"


class GPMDParser:

    def __init__(self, data: array.array):
        self.data = data

    def items(self):
        offset = 0
        while offset < len(self.data):
            item = self.from_array(self.data, offset)
            yield item
            offset += item.bytecount

    def from_array(self, data, offset):
        fourcc, type_char_code, size, repeat = GPMDStruct.unpack_from(data, offset=offset)
        fourcc = fourcc.decode()
        length = size * repeat
        padded_length = GPMDParser.extend(length)

        if type_char_code != 0 and padded_length >= 0:
            s = struct.Struct('>' + str(padded_length) + 's')
            rawdata, = s.unpack_from(data, offset=offset + 8)

            return GPMDItem(fourcc, type_char_code, size, repeat, padded_length, rawdata)
        else:
            offset += GPMDStruct.size
            child_data = data[offset:padded_length + offset]

            children = []

            child_offset = 0

            while child_offset < len(child_data):
                child = self.from_array(child_data, child_offset)
                children.append(child)
                child_offset += child.bytecount

            return GPMDContainer(fourcc, size, repeat, padded_length, children)

    @staticmethod
    def extend(n, base=4):
        i = n
        while i % base != 0:
            i += 1
        return i


class GoproMeta:

    def __init__(self, items):
        self._items = items

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        return self._items[key]

    def accept(self, visitor):
        for item in self._items:
            item.accept(visitor)
        return visitor

    @staticmethod
    def parse(data) -> 'GoproMeta':
        return GoproMeta(list(GPMDParser(data).items()))
