import dataclasses
import functools


@functools.total_ordering
@dataclasses.dataclass
class Reading:
    v: float

    def value(self):
        return max(0.0, min(1.0, self.v))

    @staticmethod
    def full():
        return Reading(1.0)

    def __eq__(self, other):
        if not type(other) == Reading:
            return NotImplemented
        return self.v == other.v

    def __lt__(self, other):
        if not type(other) == Reading:
            return NotImplemented
        return self.v < other.v
