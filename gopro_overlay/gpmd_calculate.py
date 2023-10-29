from typing import Optional, Any, Callable, Tuple

from gopro_overlay.exceptions import Defect
from gopro_overlay.ffmpeg_gopro import MetaMeta
from gopro_overlay.gpmd import GPMD
from gopro_overlay.gpmd_visitors import CorrectionFactors, DetermineTimestampOfFirstSHUTVisitor, \
    CalculateCorrectionFactorsVisitor
from gopro_overlay.log import log
from gopro_overlay.timeunits import Timeunit, timeunits

class PacketTimeCalculator:
    def next_packet(self, timestamp: int, samples_before_this: int, num_samples: int) -> Callable[[int], Tuple[Timeunit, Timeunit]]:
        raise NotImplementedError()

class CoriTimestampPacketTimeCalculator(PacketTimeCalculator):
    def __init__(self, cori_timestamp: Timeunit):
        self._cori_timestamp = cori_timestamp
        self._first_timestamp: Optional[Timeunit] = None
        self._last_timestamp: Optional[Timeunit] = None
        self._adjust: Optional[Timeunit] = None

    def next_packet(self, timestamp, samples_before_this, num_samples):

        if self._first_timestamp is not None and self._last_timestamp is not None and timestamp < self._last_timestamp:
            # This is definitely wrong - need all the SHUT timings from the joined files...
            self._adjust += self._last_timestamp
            log(f"Joined file detected... adjusting by {self._adjust}")
            self._first_timestamp = timestamp
            self._last_timestamp = timestamp

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


class CorrectionFactorsPacketTimeCalculator(PacketTimeCalculator):
    def __init__(self, correction_factors: CorrectionFactors):
        self.correction_factors = correction_factors

    def next_packet(self, timestamp, samples_before_this, num_samples):
        return lambda index: (
            self.correction_factors.first_frame + timeunits(
                seconds=(samples_before_this + index) / self.correction_factors.frames_s),
            timeunits(seconds=index / self.correction_factors.frames_s)
        )


class UnknownPacketTimeCalculator(PacketTimeCalculator):
    def __init__(self, packet_type):
        self._packet_type = packet_type

    def next_packet(self, timestamp, samples_before_this, num_samples):
        raise Defect("can't calculate timings for {self._packet_type} as none were seen.")


def timestamp_calculator_for_packet_type(meta: GPMD, metameta: MetaMeta, packet_type: str) -> PacketTimeCalculator:
    cori_timestamp = meta.accept(DetermineTimestampOfFirstSHUTVisitor()).timestamp
    if cori_timestamp is not None:
        return CoriTimestampPacketTimeCalculator(cori_timestamp)
    else:
        assert metameta is not None
        visitor = CalculateCorrectionFactorsVisitor(packet_type, metameta)
        meta.accept(visitor)

        if visitor.found():
            return CorrectionFactorsPacketTimeCalculator(visitor.factors())
        else:
            # assume that processing of same packet will follow, and not find any...
            return UnknownPacketTimeCalculator(packet_type)
