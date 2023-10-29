import dataclasses
import datetime


@dataclasses.dataclass(frozen=True)
class DateRange:
    start: datetime.datetime
    end: datetime.datetime

    def total_seconds(self):
        return (self.end - self.start).total_seconds()

    def overlap_seconds(self, other: 'DateRange'):
        latest_start = max(self.start, other.start)
        earliest_end = min(self.end, other.end)
        delta = (earliest_end - latest_start).total_seconds()
        return int(max(0.0, delta))
