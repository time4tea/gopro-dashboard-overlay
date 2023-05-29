import ctypes
import multiprocessing
from multiprocessing.shared_memory import SharedMemory

import pytest
from PIL import Image, ImageDraw

from gopro_overlay.buffering import Frame
from gopro_overlay.dimensions import Dimension
from tests.approval import approve_image

size = Dimension(256, 256)
buffer_size = (size.x * size.y * 4)


@pytest.fixture(scope="class")
def shm():
    shm_size = buffer_size * 1
    shm = SharedMemory(create=True, name="test", size=shm_size)
    yield shm
    shm.close()
    shm.unlink()


@pytest.fixture(scope="class")
def quit_flag():
    flag = multiprocessing.Value(ctypes.c_int)
    yield flag


@pytest.mark.gfx
@approve_image
def test_drawing_frame_simple(shm, quit_flag):
    bg = (0, 0, 0, 0)
    with Frame(shm, quit_flag, size, bg, 0) as frame:
        def doit(image: Image.Image):
            draw = ImageDraw.Draw(image)
            draw.line((0, 0, 255, 255), (255, 0, 0), 5)

        frame.draw(doit)
        return frame.copy()


@pytest.mark.gfx
@approve_image
def test_drawing_frame_custom_background(shm, quit_flag):
    bg = (255, 0, 0, 129)
    with Frame(shm, quit_flag, size, bg, 0) as frame:
        def doit(image: Image.Image):
            draw = ImageDraw.Draw(image)
            draw.line((0, 0, 255, 255), (255, 255, 0), 5)

        frame.draw(doit)
        return frame.copy()
