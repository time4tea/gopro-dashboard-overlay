import collections
from typing import Callable, Tuple, Optional

from gopro_overlay.exceptions import Defect
from gopro_overlay.ffmpeg_gopro import DataStream
from gopro_overlay.gpmf import GPMD
from gopro_overlay.gpmf.visitors.find import DetermineTimestampOfFirstSHUTVisitor
from gopro_overlay.log import log
from gopro_overlay.timeunits import Timeunit, timeunits

CorrectionFactors = collections.namedtuple("CorrectionFactors", ["first_frame", "last_frame", "frames_s"])


class PacketTimeCalculator:
    def next_packet(self, timestamp: Timeunit, samples_before_this: int, num_samples: int) -> Callable[[int], Tuple[Timeunit, Timeunit]]:
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


def timestamp_calculator_for_packet_type(meta: GPMD, datastream: Optional[DataStream],
                                         packet_type: str) -> PacketTimeCalculator:
    cori_timestamp = meta.accept(DetermineTimestampOfFirstSHUTVisitor()).timestamp
    if cori_timestamp is not None:
        return CoriTimestampPacketTimeCalculator(cori_timestamp)
    else:
        assert datastream is not None
        visitor = CalculateCorrectionFactorsVisitor(packet_type, datastream)
        meta.accept(visitor)

        if visitor.found():
            return CorrectionFactorsPacketTimeCalculator(visitor.factors())
        else:
            # assume that processing of same packet will follow, and not find any...
            return UnknownPacketTimeCalculator(packet_type)


class PayloadMaths:
    def __init__(self, datastream: DataStream):
        self._datastream = datastream
        self._max_time = datastream.frame_count * datastream.frame_duration / datastream.timebase

    def time_of_out_packet(self, packet_number):
        packet_time = (packet_number + 1) * self._datastream.frame_duration / self._datastream.timebase
        return min(packet_time, self._max_time)


class CalculateCorrectionFactorsVisitor:
    """This implements GetGPMFSampleRate in GPMF_utils.c"""

    def __init__(self, wanted: str, datastream: DataStream):
        self.wanted = wanted
        self.wanted_method_name = f"vi_{self.wanted}"
        self._payload_maths = PayloadMaths(datastream)
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

    def found(self) -> bool:
        """indicate if we found any of the requested packet. might be one that's not present in this stream"""
        return self.count > 0

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
