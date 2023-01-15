import dataclasses
import datetime
from typing import List

from pint import Quantity

from gopro_overlay.entry import Entry
from gopro_overlay.gpmd import VECTOR
from gopro_overlay.point import PintPoint3


@dataclasses.dataclass(frozen=True)
class GRAVComponents:
    vectors: List[VECTOR]
    timestamp: int
    samples: int



class GRAVComponentConverter:

    def __init__(self, frame_calculator, units, on_item):
        self._frame_calculator = frame_calculator
        self._units = units
        self._on_item = on_item
        self._total_samples = 0

    def convert(self, counter: int, components: GRAVComponents):

        if len(components.vectors) == 0:
            return

        sample_time_calculator = self._frame_calculator.next_packet(
            components.timestamp,
            self._total_samples,
            len(components.vectors)
        )

        unit = self._units.number

        for index, vector in enumerate(components.vectors):
            sample_frame_timestamp, _ = sample_time_calculator(index)

            point_datetime = datetime.datetime.fromtimestamp(sample_frame_timestamp.millis() / 1000, datetime.timezone.utc)

            grav_vector = PintPoint3(x=self._units.Quantity(vector.a, unit), y=self._units.Quantity(-vector.c, unit), z=self._units.Quantity(-vector.b, unit))

            self._on_item(
                sample_frame_timestamp,
                Entry(
                    dt=point_datetime,
                    timestamp=self._units.Quantity(sample_frame_timestamp.millis(), self._units.number),
                    packet=self._units.Quantity(counter, self._units.number),
                    packet_index=self._units.Quantity(index, self._units.number),
                    grav=grav_vector,
                )
            )
        self._total_samples += len(components.vectors)


class GRAVStreamVisitor:

    def __init__(self, on_end):
        self.on_end = on_end
        self._scale = None
        self._grav = None

    def vi_STMP(self, item):
        self._timestamp = item.interpret()

    def vi_TSMP(self, item):
        self._samples_total = item.interpret()

    def vi_SCAL(self, item):
        self._scale = item.interpret()

    def vi_GRAV(self, item):
        self._grav = item.interpret(self._scale)

    def v_end(self):
        self.on_end(
            GRAVComponents(self._grav, self._timestamp, self._samples_total)
        )


# noinspection PyPep8Naming
class GRAVisitor:

    def __init__(self, on_item=lambda counter, components: None):
        self._counter = 0
        self._on_item = on_item

    def vic_DEVC(self, i, s):
        self._counter += 1
        return self

    def vic_STRM(self, i, s):
        if "GRAV" in s:
            return GRAVStreamVisitor(on_end=lambda components: self._on_item(self._counter, components))

    def v_end(self):
        pass
