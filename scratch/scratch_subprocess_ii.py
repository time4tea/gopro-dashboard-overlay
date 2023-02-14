import contextlib
import ctypes
import dataclasses
import multiprocessing
import os
from multiprocessing import shared_memory
from pathlib import Path

from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGOverlay
from gopro_overlay.font import load_font
from gopro_overlay.widgets.text import Text


def raw_image(dimensions: Dimension, buffer) -> Image.Image:
    image = Image.frombuffer("RGBA", (dimensions.x, dimensions.y), buffer, "raw", "RGBA", 0, 1)
    image.readonly = 0
    return image


def clear_buffer(buffer, offset, l):
    ctypes.memset(ctypes.byref(buffer[offset:]), 0x00, l)


class Scene:

    def __init__(self, widgets):
        self._widgets = widgets

    def draw(self, image: Image):
        draw = ImageDraw.Draw(image)

        for w in self._widgets:
            w.draw(image, draw)


@dataclasses.dataclass(frozen=True)
class FrameBuffer:
    image: Image
    can_write: multiprocessing.Condition
    can_draw: multiprocessing.Condition


class DoubleBuffer:

    def __init__(self, dimension: Dimension):
        self.dimension = dimension

        self.buffer_size = (dimensions.x * dimensions.y * 4)
        self.buffer = None
        self.shm = None

        self.quit = multiprocessing.Value(ctypes.c_int)

    def writer(self, name: str, io, offset, frame: ctypes.c_long, framebuffer: FrameBuffer):

        expected_frame = 0

        while True:
            with framebuffer.can_write:
                while True:
                    if not framebuffer.can_write.wait_for(lambda: (frame.value == expected_frame) or self.quit.value == True, timeout=0.1):
                        if self.quit.value == 1:
                            print(f"{name} Exiting")
                            exit()
                    else:
                        break

            if self.quit.value == 1:
                print(f"{name} Exiting")
                exit()

            print(f"{name} Writing.....{frame.value}")
            io.write(shm.buf[offset:self.buffer_size])
            clear_buffer(self.buffer, offset, buffer_size)

            expected_frame += 1

            with framebuffer.can_draw:
                framebuffer.can_draw.notify()

    @contextlib.contextmanager
    def do(self, io):
        self.shm = shared_memory.SharedMemory(create=True, name=shm_name, size=buffer_size * 2)
        self.buffer = ctypes.c_char.from_buffer(shm.buf)

        frame_a_counter = multiprocessing.Value(ctypes.c_long)
        frame_b_counter = multiprocessing.Value(ctypes.c_long)

        try:
            with raw_image(dimensions, shm.buf[:self.buffer_size]) as image1:
                with raw_image(dimensions, shm.buf[self.buffer_size:]) as image2:

                    framebuffer_a = FrameBuffer(image1, multiprocessing.Condition, multiprocessing.Condition)
                    framebuffer_b = FrameBuffer(image2, multiprocessing.Condition, multiprocessing.Condition)

                    workerA = multiprocessing.Process(target=self.writer, args=("worker1", io, 0, frame_a_counter, framebuffer_a))
                    workerA.start()

                    workerB = multiprocessing.Process(target=self.writer, args=("worker1", io, buffer_size, frame_b_counter, framebuffer_b))
                    workerB.start()

                    try:
                        yield self
                    finally:
                        self.quit.value = 1

                        workerA.join(2)
                        if workerA.exitcode is None:
                            print("Yikes - worker A didn't finish")
                        else:
                            print("Worker A finished")

                        workerB.join(2)
                        if workerB.exitcode is None:
                            print("Yikes - worker B didn't finish")
                        else:
                            print("Worker B finished")
        finally:
            shm.close()
            shm.unlink()


if __name__ == "__main__":
    dimensions = Dimension(2704, 1520)
    buffer_size = (dimensions.x * dimensions.y * 4)

    shm_name = f"gopro.{os.getpid()}"
    shm = shared_memory.SharedMemory(create=True, name=shm_name, size=buffer_size * 2)

    font = load_font("Roboto-Medium.ttf")

    frame = multiprocessing.Value(ctypes.c_long)

    frame.value = -1

    counter = 0

    scene = Scene(
        widgets=[
            Text(dimensions / 2, value=lambda: f"{counter}", align="mb", font=font.font_variant(size=320))
        ]
    )

    ffmpeg = FFMPEGOverlay(output=Path("file.MP4"), overlay_size=dimensions)

    double_buffer = DoubleBuffer(dimensions)

    with ffmpeg.generate() as writer:
        with double_buffer.do(writer) as alternator:
            pass
