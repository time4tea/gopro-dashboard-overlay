import timeit
from typing import Callable

import _freetype


class FreeTypeImageCache:

    def __init__(self, ptr):
        # ptr = FTC_ImageCache
        self.ptr = ptr


class FreeTypeFontSize:

    def __init__(self, ptr, imagecache: FreeTypeImageCache):
        # ptr = FT_SizeRec
        self.ptr = ptr
        self.imagecache = imagecache

    def render(self, string: str):
        _freetype.render_render_string(self.ptr, self.imagecache.ptr, string)

    def __str__(self) -> str:
        return f"SizeRec: {self.ptr}"


class FreeTypeFontId:
    def __init__(self, id):
        self.id = id


class FreeTypeCacheManager:

    def __init__(self, library):
        # ptr = FTC_Manager
        self.ptr = _freetype.cache_manager_new(library.ptr, self._id_to_path)
        self.bitcacheptr = _freetype.bit_cache_new(self.ptr)
        self.known = {}
        self.counter = 0

    def _id_to_path(self, id):
        path = self.known[id]
        print(f"Returning {path}")
        return path

    def render(self, font_id: FreeTypeFontId, string: str, cb: Callable, width: int = 0, height: int = 0):
        _freetype.render_render_string(self.ptr, self.bitcacheptr, font_id.id, width, height, string, cb)

    def register_font(self, path) -> FreeTypeFontId:
        if path in self.known:
            id = self.known[path]
        else:
            self.counter += 1
            id = self.counter
            self.known[id] = path

        return FreeTypeFontId(id)

    def __enter__(self):
        if self.ptr is None:
            raise AssertionError("No handle")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _freetype.cache_manager_done(self.ptr)
        self.ptr = None


class FreeType:

    def __init__(self):
        # ptr = FT_Library
        self.ptr = _freetype.freetype_init()

    def version(self):
        return _freetype.freetype_version(self.ptr)

    def create_cache(self):
        return FreeTypeCacheManager(self)

    def __enter__(self):
        if self.ptr is None:
            raise AssertionError("No handle")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _freetype.freetype_done(self.ptr)
        self.ptr = None


if __name__ == "__main__":

    time_unit = None
    units = {"nsec": 1e-9, "usec": 1e-6, "msec": 1e-3, "sec": 1.0}


    def format_time(dt):
        unit = time_unit

        if unit is not None:
            scale = units[unit]
        else:
            scales = [(scale, unit) for unit, scale in units.items()]
            scales.sort(reverse=True)
            for scale, unit in scales:
                if dt >= scale:
                    break

        return "%.*g %s" % (3, dt / scale, unit)


    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (800, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)


    class WidthCalc:

        def __init__(self):
            self.x = 0

        def font_callback(self, width, height, left, top, format, max_grays, pitch, xadvance, yadvance, mv):
            for j in range(0, height):
                for i in range(0, width):
                    v = mv[(j * pitch) + i]
                    image.putpixel((self.x + i, j), (v, v, v))
            self.x += xadvance


    renderable = "Date: 2022-09-26 Time: 14:35:26.1"

    with FreeType() as ft:
        print(ft.version())

        with ft.create_cache() as cache:
            id = cache.register_font("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf")
            cache.render(id, renderable, height=40, cb=WidthCalc().font_callback)

            # time_count = 1000
            # time_take = timeit.timeit(lambda: cache.render(id, renderable, height=40, cb=WidthCalc().font_callback), number=time_count)
            # print(time_take)
            # print(format_time(time_take / time_count))


    image.show()
