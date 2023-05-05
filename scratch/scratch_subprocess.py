import ctypes
import multiprocessing
import os
from multiprocessing import shared_memory
from pathlib import Path

from PIL import Image, ImageDraw

from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGOverlay
from gopro_overlay.font import load_font
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.text import Text


def raw_image(dimensions: Dimension, buffer) -> Image.Image:
    image = Image.frombuffer("RGBA", (dimensions.x, dimensions.y), buffer, "raw", "RGBA", 0, 1)
    image.readonly = 0
    return image

def clear_buffer(buffer,l):
    ctypes.memset(ctypes.byref(buffer), 0x00, l)

def p_writer(shm, buffer_size, frame, quit, writer, condition_can_write: multiprocessing.Condition, condition_can_draw):

    expected_frame = 0

    ctypes_buffer = ctypes.c_char.from_buffer(shm.buf)

    while True:
        with condition_can_write:
            while True:
                if not condition_can_write.wait_for(lambda : (frame.value == expected_frame) or quit.value == True, timeout=0.1):
                    if quit.value == 1:
                        print("Exiting")
                        exit()
                else:
                    break

        if quit.value == 1:
            print("Exiting")
            exit()

        writer.write(shm.buf[:buffer_size])
        writer.flush()
        clear_buffer(ctypes_buffer, buffer_size)

        expected_frame += 1

        with condition_can_draw:
            condition_can_draw.notify()



class Scene:

    def __init__(self, widgets):
        self._widgets = widgets

    def draw(self, image: Image):
        draw = ImageDraw.Draw(image)

        for w in self._widgets:
            w.draw(image, draw)



if __name__ == "__main__":
    dimensions = Dimension(2704, 1520)
    buffer_size = (dimensions.x * dimensions.y * 4)

    shm_name = f"gopro.{os.getpid()}"
    shm = shared_memory.SharedMemory(create=True, name=shm_name, size=buffer_size * 2)

    font = load_font("Roboto-Medium.ttf")

    condition_can_write = multiprocessing.Condition()
    condition_can_draw = multiprocessing.Condition()
    frame = multiprocessing.Value(ctypes.c_long)
    quit = multiprocessing.Value(ctypes.c_int)

    frame.value = -1

    try:
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

                worker = multiprocessing.Process(target=p_writer, args=(shm, buffer_size, frame, quit, writer, condition_can_write, condition_can_draw))
                worker.start()

                for i in range(200):

                    if not worker.is_alive():
                        print("Worked died")
                        break

                    scene.draw(image)
                    with condition_can_write:
                        frame.value = i
                        condition_can_write.notify()


                    with condition_can_draw:
                        while True:
                            if not condition_can_draw.wait(timeout=0.1):
                                if not worker.is_alive():
                                    break
                            else:
                                break

                    counter += 1

                print("done")
                quit.value = 1
                with condition_can_write:
                    condition_can_write.notify()

        finally:
            image.close()

    finally:
        shm.close()
        shm.unlink()
