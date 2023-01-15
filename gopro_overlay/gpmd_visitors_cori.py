import dataclasses
import datetime
from typing import List, Optional

from pint import Quantity

from gopro_overlay.entry import Entry
from gopro_overlay.gpmd import QUATERNION
from gopro_overlay.point import Quaternion, Point3, EulerRadians


@dataclasses.dataclass(frozen=True)
class CORIComponents:
    orientations: List[QUATERNION]
    timestamp: int
    samples: int


@dataclasses.dataclass(frozen=True)
class Orientation:
    roll: Quantity
    pitch: Quantity
    yaw: Quantity


def euler_to_orientation(e: EulerRadians, units) -> Orientation:
    radians = units.radians
    return Orientation(
        roll=units.Quantity(e.roll, radians),
        pitch=units.Quantity(e.pitch, radians),
        yaw=units.Quantity(e.yaw, radians)
    )


class CORIComponentConverter:

    def __init__(self, frame_calculator, units, on_item):
        self._frame_calculator = frame_calculator
        self._units = units
        self._on_item = on_item
        self._total_samples = 0

    def convert(self, counter: int, components: CORIComponents):

        if len(components.orientations) == 0:
            return

        sample_time_calculator = self._frame_calculator.next_packet(
            components.timestamp,
            self._total_samples,
            len(components.orientations)
        )

        for index, cori in enumerate(components.orientations):
            sample_frame_timestamp, _ = sample_time_calculator(index)

            point_datetime = datetime.datetime.fromtimestamp(sample_frame_timestamp.millis() / 1000, tz=datetime.timezone.utc)

            quat = Quaternion(
                w=cori.w,
                v=Point3(x=cori.x, y=cori.y, z=cori.z)
            )

            self._on_item(
                sample_frame_timestamp,
                Entry(
                    dt=point_datetime,
                    timestamp=self._units.Quantity(sample_frame_timestamp.millis(), self._units.number),
                    packet=self._units.Quantity(counter, self._units.number),
                    packet_index=self._units.Quantity(index, self._units.number),
                    cori=quat,
                    ori=euler_to_orientation(
                        e=quat.euler(),
                        units=self._units
                    ),
                )
            )
        self._total_samples += len(components.orientations)


class CORIStreamVisitor:

    def __init__(self, on_end):
        self.on_end = on_end
        self._scale: Optional[int] = None
        self._cori: Optional[List[QUATERNION]] = None

    def vi_STMP(self, item):
        self._timestamp = item.interpret()

    def vi_TSMP(self, item):
        self._samples_total = item.interpret()

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_CORI(self, item):
        self._cori = item.interpret(self._scale)

    def v_end(self):
        self.on_end(
            CORIComponents(self._cori, self._timestamp, self._samples_total)
        )


# noinspection PyPep8Naming
class CORIVisitor:

    def __init__(self, on_item=lambda counter, components: None):
        self._counter = 0
        self._on_item = on_item

    def vic_DEVC(self, i, s):
        self._counter += 1
        return self

    def vic_STRM(self, i, s):
        if "CORI" in s:
            return CORIStreamVisitor(on_end=lambda components: self._on_item(self._counter, components))

    def v_end(self):
        pass
