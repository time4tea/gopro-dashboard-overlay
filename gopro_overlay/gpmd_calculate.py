from typing import Optional

from gopro_overlay.gpmd_visitors import CorrectionFactors
from gopro_overlay.timeunits import Timeunit, timeunits


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
