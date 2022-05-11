import array
import collections
import datetime
import itertools
import struct
from enum import Enum
from typing import Optional

from .entry import Entry
from .ffmpeg import MetaMeta
from .point import Point, Point3
from .timeunits import timeunits, Timeunit

GPMDStruct = struct.Struct('>4sBBH')

GPS5 = collections.namedtuple("GPS5", "lat lon alt speed speed3d")
XYZ = collections.namedtuple('XYZ', "y x z")
VECTOR = collections.namedtuple("VECTOR", "x y z")
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
    return item.rawdata.decode('utf-8', errors='replace').strip('\0')


def _interpret_gps_timestamp(item, *args):
    return datetime.datetime.strptime(item.rawdata.decode('utf-8', errors='replace'), '%y%m%d%H%M%S.%f').replace(
        tzinfo=datetime.timezone.utc)


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


def _interpret_gps5(item, scale):
    return [GPS5._make(it) for it in _interpret_element(item, scale)]


def _interpret_gps_precision(item, *args):
    return _interpret_atom(item) / 100.0


def _interpret_xyz(item, scale):
    return [XYZ._make(it) for it in _interpret_element(item, scale)]


def _interpret_vector(item, scale):
    return [VECTOR._make(it) for it in _interpret_element(item, scale)]


def _interpret_quaternion(item, scale):
    return [QUATERNION._make(it) for it in _interpret_element(item, scale)]


def _interpret_gps_lock(item, *args):
    return GPSFix(_interpret_atom(item))


def _interpret_stream_marker(item, *args):
    return "Stream Marker"


def _interpret_device_marker(item, *args):
    return "Device Marker"


interpreters = {
    "ACCL": _interpret_xyz,
    "DEVC": _interpret_device_marker,
    "DVNM": _interpret_string,
    "GPS5": _interpret_gps5,
    "GPSF": _interpret_gps_lock,
    "GPSP": _interpret_gps_precision,
    "GPSU": _interpret_gps_timestamp,
    "GYRO": _interpret_xyz,
    "MWET": _interpret_list,
    "SCAL": _interpret_list,
    "SIUN": _interpret_string,
    "STMP": _interpret_timestamp,
    "TMPC": _interpret_atom,
    "STNM": _interpret_string,
    "STRM": _interpret_stream_marker,
    "TSMP": _interpret_atom,
    "TICK": _interpret_atom,
    "TOCK": _interpret_atom,
    "GRAV": _interpret_vector,
    "WNDM": _interpret_list,
    "CORI": _interpret_quaternion,
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
    def parse(data):
        return GoproMeta(list(GPMDParser(data).items()))


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


XYZComponents = collections.namedtuple("XYZComponents", ["timestamp", "samples_total", "scale", "temp", "points"])


# noinspection PyPep8Naming
class XYZStreamVisitor:

    def __init__(self, on_end):
        self._on_end = on_end
        self._samples_total = None
        self._timestamp = None
        self._scale = None
        self._temperature = None
        self._type = None
        self._points = None

    def vi_STMP(self, item):
        self._timestamp = item.interpret()

    def vi_TSMP(self, item):
        self._samples_total = item.interpret()

    def vi_ORIN(self, item):
        pass

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_TMPC(self, item):
        self._temperature = item.interpret()

    def vi_ACCL(self, item):
        self._type = item.fourcc
        self._points = item.interpret(self._scale)

    def vi_GYRO(self, item):
        self._type = item.fourcc
        self._points = item.interpret(self._scale)

    def v_end(self):
        self._on_end(
            XYZComponents(
                timestamp=self._timestamp,
                samples_total=self._samples_total,
                scale=self._scale,
                temp=self._temperature,
                points=self._points,
            )
        )


class XYZComponentConverter:

    def __init__(self, on_item):
        self._on_item = on_item

    def convert(self, counter, components):
        for index, point in enumerate(components.points):
            self._on_item((counter, index, Point3(point.x, point.y, point.z)))


# noinspection PyPep8Naming
class XYZVisitor:

    def __init__(self, name, on_item):
        self._counter = 0
        self._name = name
        self._on_item = on_item

    def vic_DEVC(self, item, contents):
        self._counter += 1
        return self

    def vic_STRM(self, item, contents):
        if self._name in contents:
            return XYZStreamVisitor(on_end=lambda i: self._on_item(self._counter, i))

    def v_end(self):
        pass


GPS5Components = collections.namedtuple("GPS5Components",
                                        ["samples", "timestamp", "basetime", "fix", "dop", "scale", "points"])


# noinspection PyPep8Naming
class GPS5StreamVisitor:

    def __init__(self, on_end):
        self._on_end = on_end
        self._samples = None
        self._basetime = None
        self._fix = None
        self._scale = None
        self._points = None
        self._timestamp = None

    def vi_STMP(self, item):
        self._timestamp = interpret_item(item)

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
        self._points = interpret_item(item, self._scale)

    def v_end(self):
        self._on_end(GPS5Components(
            samples=self._samples,
            timestamp=self._timestamp,
            basetime=self._basetime,
            fix=self._fix,
            dop=self._dop,
            scale=self._scale,
            points=self._points
        ))


# noinspection PyPep8Naming
class GPSVisitor:

    def __init__(self, converter):
        self._converter = converter
        self._counter = 0

    def vic_DEVC(self, item, contents):
        return self

    def vic_STRM(self, item, contents):
        if "GPS5" in contents:
            return GPS5StreamVisitor(
                on_end=lambda c: self._converter(self._counter, c)
            )

    def v_end(self):
        self._counter += 1
        pass


class PayloadMaths:
    def __init__(self, metameta: MetaMeta):
        self._metameta = metameta
        self._max_time = metameta.frame_count * metameta.frame_duration / metameta.timebase

    def time_of_out_packet(self, packet_number):
        packet_time = (packet_number + 1) * self._metameta.frame_duration / self._metameta.timebase
        return min(packet_time, self._max_time)


CorrectionFactors = collections.namedtuple("CorrectionFactors", ["first_frame", "last_frame", "frames_s"])


class CalculateCorrectionFactorsVisitor:
    """This implements GetGPMFSampleRate in GPMF_utils.c"""

    def __init__(self, wanted, metameta: MetaMeta):
        self.wanted = wanted
        self.wanted_method_name = f"vi_{self.wanted}"
        self._payload_maths = PayloadMaths(metameta)
        self.count = 0
        self.samples = 0
        self.meanY = 0
        self.meanX = 0
        self.repeatarray = []

    def vic_DEVC(self, item, contents):
        return self

    def __getattr__(self, name, *args):
        if name == self.wanted_method_name:
            return self._handle_item
        else:
            raise AttributeError(f"{name}")

    def vic_STRM(self, item, contents):
        if self.wanted in contents:
            return self

    def _handle_item(self, item):
        self.samples += item.repeat
        self.meanY += self.samples
        self.meanX += self._payload_maths.time_of_out_packet(self.count)
        self.repeatarray.append(self.samples)
        self.count += 1

    def v_end(self):
        pass

    # no idea how this works, but the numbers that come out of it are the same numbers as in GPMF_utils.c
    def factors(self):
        meanY = self.meanY / self.count
        meanX = self.meanX / self.count

        top = 0
        bottom = 0
        for index, sample in enumerate(self.repeatarray):
            time_of_out_packet = self._payload_maths.time_of_out_packet(index)
            top += (time_of_out_packet - meanX) * (sample - meanY)
            bottom += (time_of_out_packet - meanX) * (time_of_out_packet - meanX)

        slope = top / bottom
        rate = slope

        intercept = meanY - slope * meanX
        first = -intercept / rate
        last = first + self.samples / rate

        return CorrectionFactors(
            first_frame=timeunits(seconds=first),
            last_frame=timeunits(seconds=last),
            frames_s=rate
        )


class GPS5EntryConverter:

    def __init__(self, units, drop_item=lambda t, c: False, on_item=lambda e: None):
        self._units = units
        self._drop_item = drop_item
        self._on_item = on_item

    def convert(self, counter, components):
        if not self._drop_item(counter, components):
            for index, point in enumerate(components.points):
                point_datetime = components.basetime + datetime.timedelta(
                    seconds=(index * (1.0 / len(components.points)))
                )
                self._on_item(
                    Entry(
                        dt=point_datetime,
                        dop=self._units.Quantity(components.dop, self._units.location),
                        packet=self._units.Quantity(counter, self._units.location),
                        packet_index=self._units.Quantity(index, self._units.location),
                        point=Point(point.lat, point.lon),
                        speed=self._units.Quantity(point.speed, self._units.mps),
                        alt=self._units.Quantity(point.alt, self._units.m),
                        gpsfix=components.fix
                    )
                )


class CoriTimestampPacketTimeCalculator:
    def __init__(self, cori_timestamp: Timeunit):
        self._cori_timestamp = cori_timestamp
        self._first_timestamp: Optional[Timeunit] = None
        self._last_timestamp: Optional[Timeunit] = None
        self._adjust: Optional[Timeunit] = None

    def next_packet(self, timestamp, samples_before_this, num_samples):
        if self._first_timestamp is None:
            self._first_timestamp = timestamp
            self._adjust = timestamp - self._cori_timestamp

        if self._last_timestamp is None:
            self._last_timestamp = timestamp
            time_per_sample = timeunits(millis=1001) / num_samples
        else:
            time_per_sample = (timestamp - self._last_timestamp) / num_samples
            self._last_timestamp = timestamp

        return lambda index: (
            timestamp + self._adjust - self._first_timestamp + (index * time_per_sample), index * time_per_sample
        )


class CorrectionFactorsPacketTimeCalculator:
    def __init__(self, correction_factors: CorrectionFactors):
        self.correction_factors = correction_factors

    def next_packet(self, timestamp, samples_before_this, num_samples):
        return lambda index: (
            self.correction_factors.first_frame + timeunits(
                seconds=(samples_before_this + index) / self.correction_factors.frames_s),
            timeunits(seconds=index / self.correction_factors.frames_s)
        )


class NewGPS5EntryConverter:
    def __init__(self, units, calculator, on_item=lambda c, e: None):
        self._units = units
        self._on_item = on_item
        self._total_samples = 0
        self._frame_calculator = calculator

    def convert(self, counter, components):
        sample_time_calculator = self._frame_calculator.next_packet(
            components.timestamp,
            self._total_samples,
            len(components.points)
        )

        for index, point in enumerate(components.points):
            sample_frame_timestamp, sample_time_offset = sample_time_calculator(index)

            point_datetime = components.basetime + datetime.timedelta(
                microseconds=sample_time_offset.us
            )
            self._on_item(
                sample_frame_timestamp,
                Entry(
                    dt=point_datetime,
                    timestamp=self._units.Quantity(sample_frame_timestamp.millis(), self._units.number),
                    dop=self._units.Quantity(components.dop, self._units.number),
                    packet=self._units.Quantity(counter, self._units.number),
                    packet_index=self._units.Quantity(index, self._units.number),
                    point=Point(point.lat, point.lon),
                    speed=self._units.Quantity(point.speed, self._units.mps),
                    alt=self._units.Quantity(point.alt, self._units.m),
                    gpsfix=components.fix.value
                )
            )
        self._total_samples += len(components.points)

    # noinspection PyPep8Naming


class DetermineTimestampOfFirstSHUTVisitor:
    """
        Seems like first SHUT frame is correlated with video frame?
        https://github.com/gopro/gpmf-parser/blob/151bb352ab3d1af8feb31e0cf8277ff86c70095d/demo/GPMF_demo.c#L414
    """

    def __init__(self):
        self._initial_timestamp = None

    @property
    def timestamp(self):
        return self._initial_timestamp

    def vic_DEVC(self, item, contents):
        if not self._initial_timestamp:
            return self

    def vi_STMP(self, item):
        self._initial_timestamp = interpret_item(item)

    def vic_STRM(self, item, contents):
        if "SHUT" in contents and not self._initial_timestamp:
            return self

    def v_end(self):
        pass


class DebuggingVisitor:

    def __init__(self):
        self._indent = 0

    def __getattr__(self, item):
        if item.startswith("vi_"):
            return lambda a: print(f"{' ' * self._indent}{a}")
        if item.startswith("vic_"):
            def thing(a, b):
                print(f"{' ' * self._indent}{a}")
                self._indent += 1

                return self

            return thing
        raise AttributeError(item)

    def v_end(self):
        self._indent -= 1
