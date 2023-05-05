import ctypes
import multiprocessing
import os
from io import BytesIO
from multiprocessing import shared_memory
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGOverlay
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


class Frame:

    def __init__(self, shm: SharedMemory, size: int, count: int):
        self.shm = shm
        self.size = size
        self.count = count
        self.active = multiprocessing.Lock()
        self.can_draw = multiprocessing.Condition(self.active)
        self.can_write = multiprocessing.Condition(self.active)

        self.ctypes_buffer = ctypes.c_char.from_buffer(shm.buf)

        self.drawn_frame_number = multiprocessing.Value(ctypes.c_long)
        self.drawn_frame_number.value = -1

        self.written_frame_number = multiprocessing.Value(ctypes.c_long)
        self.written_frame_number.value = -1

    def clear(self):
        clear_buffer(self.ctypes_buffer, buffer_size)

    def draw(self, quit: multiprocessing.Value, f: Callable):
        with self.can_draw:
            while not self.can_draw.wait_for(predicate=lambda: quit.value == 1 or self.written_frame_number.value == self.drawn_frame_number.value, timeout=cond_timeout):
                print("Waiting to draw")

        if self.drawn_frame_number.value == self.written_frame_number.value:
            f()

        self.drawn_frame_number.value += 1
        with self.can_write:
            self.can_write.notify()

        if quit.value == 1:
            return False
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.ctypes_buffer
        pass

    def write(self, writer: BytesIO, quit: multiprocessing.Value) -> bool:
        with self.can_write:
            while not self.can_write.wait_for(predicate=lambda: quit.value == 1 or self.drawn_frame_number.value > self.written_frame_number.value, timeout=cond_timeout):
                print("waiting to write")

        if self.drawn_frame_number.value > self.written_frame_number.value:
            writer.write(shm.buf[self.size * self.count:self.size * (self.count + 1)])
            writer.flush()
            self.clear()
            self.written_frame_number.value += 1

            with self.can_draw:
                self.can_draw.notify()

        if quit.value == 1:
            return False
        return True


def p_writer(frame: Frame, quit:multiprocessing.Value, writer: BytesIO):
    while True:
        if not frame.write(writer, quit):
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

    drawn_frame_number = multiprocessing.Value(ctypes.c_long)
    written_frame_number = multiprocessing.Value(ctypes.c_long)
    quit = multiprocessing.Value(ctypes.c_int)

    drawn_frame_number.value = -1
    written_frame_number.value = -1

    try:

        with Frame(shm, buffer_size, 0) as frame:

            image = raw_image(dimensions, shm.buf)
            try:

                counter = 0

                scene = Scene(
                    widgets=[
                        Text(dimensions / 2, value=lambda: f"{counter}", align="mb", font=font.font_variant(size=320))
                    ]
                )

                ffmpeg = FFMPEGOverlay(output=Path("file.MP4"), overlay_size=dimensions)

                with ffmpeg.generate() as writer:

                    worker = multiprocessing.Process(target=p_writer, args=(frame, quit, writer))
                    worker.start()

                    try:
                        for i in range(100):
                            if not worker.is_alive():
                                print("Worked died")
                                break

                            frame.draw(quit, lambda: scene.draw(image))
                            counter += 1

                        print("done")
                        quit.value = 1
                    finally:
                        worker.join(timeout=0.5)
            finally:
                image.close()

    finally:
        shm.close()
        shm.unlink()
