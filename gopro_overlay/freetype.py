import timeit
from dataclasses import dataclass
from typing import Callable, Any

import _freetype

from gopro_overlay import font


class FreeTypeFontId:
    def __init__(self, id):
        self.id = id


class FontRegistry:

    def __init__(self) -> None:
        self.known = {}
        self.counter = 0

    def path(self, id):
        return self.known[id]

    def register(self, path) -> FreeTypeFontId:
        if path in self.known:
            id = self.known[path]
        else:
            self.counter += 1
            id = self.counter
            self.known[id] = path

        return FreeTypeFontId(id)


@dataclass(frozen=True)
class Caches:
    imagecache: Any
    bitcache: Any
    cmapcache: Any


class FreeTypeCacheManager:

    def __init__(self, library):
        # ptr = FTC_Manager
        self.registry = FontRegistry()
        self.library = library
        self.ptr = _freetype.cache_manager_new(library.ptr, self.registry.path)
        self.caches = Caches(
            imagecache=_freetype.image_cache_new(self.ptr),
            bitcache=_freetype.bit_cache_new(self.ptr),
            cmapcache=_freetype.cmap_cache_new(self.ptr)
        )

    def render(self, font_id: FreeTypeFontId, string: str, cb: Callable, width: int = 0, height: int = 0):
        _freetype.render_render_string(self.ptr, self.caches.bitcache, font_id.id, width, height, string, cb)

    def render_stroker(self, font_id: FreeTypeFontId, string: str, cb: Callable, width: int = 0, height: int = 0):
        _freetype.render_render_string_stroker(self.library.ptr, self.caches.cmapcache, self.caches.imagecache, font_id.id, width, height, string, cb)

    def register_font(self, path) -> FreeTypeFontId:
        return self.registry.register(path)

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
        print("done with library")
        _freetype.freetype_done(self.ptr)
        self.ptr = None


class BlitChars:

    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.baseline = y

    def font_callback(self, width, height, left, top, format, max_grays, pitch, xadvance, yadvance, mv):
        _freetype.blit_glyph(self.image.im.id, self.x, self.baseline - top, mv, width, height, pitch)
        self.x += xadvance

    def reset(self):
        self.x = 0


class DrawChars:

    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.baseline = y

    def font_callback(self, width, height, left, top, format, max_grays, pitch, xadvance, yadvance, mv):

        points = {}

        for j in range(0, height):
            for i in range(0, width):
                v = mv[(j * pitch) + i]
                if v > 0:
                    points.setdefault(v, []).append((self.x + i, self.baseline - top + j))

        for v, p in points.items():
            draw.point(p, (v, v, v))

        self.x += xadvance

    def reset(self):
        self.x = 0


class DumpMetrics:

    def font_callback(self, *args):
        print(*args)

    def reset(self):
        pass


class Noop:
    def font_callback(self, *args):
        pass

    def reset(self):
        pass


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

    renderable = "Date: 2022-09-26 Time: 14:35:26.1"

    rendered = True

    pillow_font = font.load_font("Roboto-Medium.ttf", 40)

    def pillow_thing():
        draw.text(
                    (0, 50),
                    renderable,
                    anchor="la",
                    direction="ltr",
                    font=pillow_font,
                    fill=(255,255,255),
                    stroke_width=2,
                    stroke_fill=(0, 0, 0)
                )

    pillow_thing()

    with FreeType() as ft:
        print(ft.version())

        with ft.create_cache() as cache:
            id = cache.register_font("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf")
            # cache.render(id, renderable, height=40, cb=WidthCalc().font_callback)

            d = BlitChars(image, 0, 50)

            def thing():
                cache.render(id, renderable, height=40, cb=d.font_callback)
                d.reset()


            thing()

            print("Cache")
            time_count = 100
            time_take = timeit.timeit(thing, number=time_count)
            print(f"  {time_take}")
            print(f"  {format_time(time_take / time_count)}")

            print("Pillow")
            time_take = timeit.timeit(pillow_thing, number=time_count)
            print(f"  {time_take}")
            print(f"  {format_time(time_take / time_count)}")

    if rendered:
        image.show()
