from datetime import timedelta

from gopro_overlay import ffmpeg
from gopro_overlay.ffmpeg import MetaMeta
from gopro_overlay.framemeta import framemeta_from_meta
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.units import units
from tests.test_gpmd import DebuggingVisitor


def load_file(path):
    return GoproMeta.parse(ffmpeg.load_gpmd_from(path))


def test_debug_file():
    meta = load_file("/home/richja/dev/gopro-graphics/render/contrib/GH010278.MP4")

    visitor = DebuggingVisitor()

    meta.accept(visitor)


class PayloadMaths:
    def __init__(self, metameta: MetaMeta):
        self._metameta = metameta
        self._max_time = metameta.frame_count * metameta.frame_duration / metameta.timebase

    def time_of_out_packet(self, packet_number):
        packet_time = (packet_number + 1) * self._metameta.frame_duration / self._metameta.timebase
        return min(packet_time, self._max_time)


class SampleCountingVisitor:
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
    def best_fit(self):
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

        packet_times = []

        for index, sample in enumerate(self.repeatarray):
            packet_times.append(first + (sample / rate))

        print(f"First = {first}, Last = {last}, Rate = {rate}")


def test_try_and_follow_c_code():
    meta = load_file("/home/richja/dev/gopro-graphics/render/contrib/GH010278.MP4")

    visitor = meta.accept(
        SampleCountingVisitor("GPS5", MetaMeta(stream=3, frame_count=707, timebase=1000, frame_duration=1001)))

    visitor.best_fit()

    assert visitor.count == 526
    assert visitor.samples == 9609
    assert visitor.meanY == 2547682
    assert visitor.meanX == 138739.60100000002


def test_loading_data_by_frame():
    meta = load_file("/data/richja/gopro/GH010079.MP4")

    frames = framemeta_from_meta(meta, units=units)

    print(frames)

    print(frames.get(4013))
    print(frames.get(4065))
    print(frames.get(4030))

    print(frames.items()[-1])

    stepper = frames.stepper(timedelta(seconds=0.1))
    for step in stepper.steps():
        print(step)
