import ctypes
import io
import multiprocessing
import os
from io import BytesIO
from multiprocessing import shared_memory
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg_overlay import FFMPEGOverlay, FFMPEGOptions
from gopro_overlay.font import load_font
from gopro_overlay.widgets.text import Text


def raw_image(dimensions: Dimension, buffer) -> Image.Image:
    image = Image.frombuffer("RGBA", (dimensions.x, dimensions.y), buffer, "raw", "RGBA", 0, 1)
    image.readonly = 0
    return image


def clear_buffer(buffer, l):
    ctypes.memset(ctypes.byref(buffer), 0x00, l)


class Scene:

    def __init__(self, widgets):
        self._widgets = widgets

    def draw(self, image: Image):
        draw = ImageDraw.Draw(image)

        for w in self._widgets:
            w.draw(image, draw)


cond_timeout = 1.0


class SerialisedBytesIO(io.BufferedWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = multiprocessing.Lock()

    def write(self, __buffer) -> int:
        with self.lock:
            try:
                return super().write(__buffer)
            finally:
                super().flush()


class Frame:
    def __init__(self, shm: SharedMemory, quit: multiprocessing.Value, size: Dimension, count: int):
        self.shm = shm
        self.size = size
        self.count = count
        self.quit = quit

        self.buffer_size = (dimensions.x * dimensions.y * 4)

        self.memory = shm.buf[self.buffer_size * self.count:self.buffer_size * (self.count + 1)]

        self.image = raw_image(dimensions, self.memory)

        self.active = multiprocessing.Lock()
        self.can_draw = multiprocessing.Condition(self.active)
        self.can_write = multiprocessing.Condition(self.active)

        self.ctypes_buffer = ctypes.c_char.from_buffer(self.memory)

        self.drawn_frame_number = multiprocessing.Value(ctypes.c_long)
        self.drawn_frame_number.value = -1

        self.written_frame_number = multiprocessing.Value(ctypes.c_long)
        self.written_frame_number.value = -1

    def clear(self):
        clear_buffer(self.ctypes_buffer, buffer_size)

    def draw(self, f: Callable[[Image.Image], None]):
        with self.can_draw:
            while not self.can_draw.wait_for(predicate=lambda: self.quit.value == 1 or self.written_frame_number.value == self.drawn_frame_number.value, timeout=cond_timeout):
                print(f"Frame {self.count}: Waiting to draw")

        if self.drawn_frame_number.value == self.written_frame_number.value:
            f(self.image)

        self.drawn_frame_number.value += 1
        with self.can_write:
            self.can_write.notify()

        if self.quit.value == 1:
            return False
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.ctypes_buffer
        self.image.close()
        self.memory = None

    def write(self, writer: BytesIO) -> bool:
        with self.can_write:
            while not self.can_write.wait_for(predicate=lambda: self.quit.value == 1 or self.drawn_frame_number.value > self.written_frame_number.value, timeout=cond_timeout):
                print(f"Frame {self.count}: waiting to write")

        if self.drawn_frame_number.value > self.written_frame_number.value:
            writer.write(self.memory)
            self.clear()
            self.written_frame_number.value += 1

            with self.can_draw:
                self.can_draw.notify()

        if self.quit.value == 1:
            return False
        return True


def p_writer(frame: Frame, writer: BytesIO):
    while True:
        if not frame.write(writer):
            break
    print("Writer exiting")


if __name__ == "__main__":
    dimensions = Dimension(2704, 1520)
    buffer_size = (dimensions.x * dimensions.y * 4)

    shm_name = f"gopro.{os.getpid()}"
    shm_size = buffer_size * 2
    print(f"Shared Memory size = {shm_size}")
    shm = shared_memory.SharedMemory(create=True, name=shm_name, size=shm_size)

    font = load_font("Roboto-Medium.ttf")

    quit = multiprocessing.Value(ctypes.c_int)

    try:

        with Frame(shm, quit, dimensions, 0) as frame0:
            with Frame(shm, quit, dimensions, 1) as frame1:
                counter = 0

                scene = Scene(
                    widgets=[
                        Text(dimensions / 2, value=lambda: f"{counter}", align="mb", font=font.font_variant(size=320))
                    ]
                )

                ffmpeg_options = FFMPEGOptions(
                    input=["-hwaccel", "nvdec"],
                    output=["-vcodec", "h264_nvenc", "-rc:v", "cbr", "-b:v", "50000k", "-bf:v", "3", "-profile:v", "high", "-spatial-aq", "true", "-movflags", "faststart"]
                )

                ffmpeg = FFMPEGOverlay(output=Path("file.MP4"), overlay_size=dimensions, options=ffmpeg_options)

                with ffmpeg.generate() as writer:
                    serialised = SerialisedBytesIO(writer)

                    worker1 = multiprocessing.Process(target=p_writer, args=(frame0, serialised))
                    worker1.start()
                    worker2 = multiprocessing.Process(target=p_writer, args=(frame1, serialised))
                    worker2.start()

                    try:
                        for i in range(30):
                            if not worker1.is_alive() and worker2.is_alive():
                                print("Worker died")
                                break

                            current_frame = frame0 if i % 2 == 0 else frame1
                            current_frame.draw(lambda image: scene.draw(image))

                            counter += 1

                        print("done")
                        quit.value = 1
                    finally:
                        worker1.join(timeout=0.5)
                        worker2.join(timeout=0.5)

    finally:
        shm.close()
        shm.unlink()
