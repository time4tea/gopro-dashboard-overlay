import dataclasses
import datetime
from typing import List

from gopro_overlay.entry import Entry
from gopro_overlay.gpmd import XYZ
from gopro_overlay.point import PintPoint3


class ORIN:

    def __init__(self, conversion):
        if conversion == "ZXY":
            self.convert = lambda xyz: XYZ(x=xyz.y, y=xyz.z, z=xyz.x)
        elif conversion == "YxZ":
            self.convert = lambda xyz: XYZ(x=-xyz.y, y=xyz.x, z=xyz.z)
        elif conversion == "yXZ":
            self.convert = lambda xyz: XYZ(x=xyz.y, y=-xyz.x, z=xyz.z)
        elif conversion == "zxY":
            self.convert = lambda xyz: XYZ(x=-xyz.y, y=xyz.z, z=-xyz.x)
        elif conversion == "XzY":
            self.convert = lambda xyz: XYZ(x=xyz.x, y=xyz.z, z=-xyz.y)
        else:
            raise IOError(f"Unhandled ORIN spec: {conversion}")

    def apply(self, xyz):
        return self.convert(xyz)


@dataclasses.dataclass(frozen=True)
class XYZComponents:
    timestamp: int
    samples_total: int
    scale: int
    orin: ORIN
    siun: str
    temp: int
    points: List[XYZ]


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
        self._orin = ORIN("ZXY")
        self._siun = None

    def vi_STMP(self, item):
        self._timestamp = item.interpret()

    def vi_TSMP(self, item):
        self._samples_total = item.interpret()

    def vi_SIUN(self, item):
        self._siun = item.interpret()

    def vi_ORIN(self, item):
        self._orin = ORIN(item.interpret())

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
                orin=self._orin,
                siun=self._siun,
                temp=self._temperature,
                points=self._points,
            )
        )


units_acceleration = "m/s²"


class XYZComponentConverter:

    def __init__(self, frame_calculator, units, on_item):
        self._on_item = on_item
        self._frame_calculator = frame_calculator
        self._units = units
        self._total_samples = 0

    # This only converts 1 in 10 of the XYZ Items - they run at 200Hz, and that's too much for our needs.
    def convert(self, counter, components):
        sample_time_calculator = self._frame_calculator.next_packet(
            components.timestamp,
            self._total_samples,
            len(components.points)
        )

        if components.siun == units_acceleration:
            unit = "m/s^2"
        else:
            raise IOError(f"Unsupported units {components.siun}")

        for index, point in enumerate(components.points):
            if index % 10 != 0:
                continue
            sample_frame_timestamp, _ = sample_time_calculator(index)

            point_datetime = datetime.datetime.fromtimestamp(sample_frame_timestamp.millis() / 1000, tz=datetime.timezone.utc)

            correct_orientation = components.orin.apply(point)
            self._on_item(
                sample_frame_timestamp,
                Entry(
                    dt=point_datetime,
                    timestamp=self._units.Quantity(sample_frame_timestamp.millis(), self._units.number),
                    packet=self._units.Quantity(counter, self._units.number),
                    packet_index=self._units.Quantity(index, self._units.number),
                    accl=PintPoint3(
                        x=self._units.Quantity(correct_orientation.x, unit),
                        y=self._units.Quantity(correct_orientation.y, unit),
                        z=self._units.Quantity(correct_orientation.z, unit),
                    )
                )
            )
        self._total_samples += len(components.points)


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
