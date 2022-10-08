import timeit
from dataclasses import dataclass
from typing import Any, Tuple

import _freetype
from PIL.Image import Image

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


@dataclass(frozen=True)
class BBox:
    x: int
    y: int


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

    def calculate_size(self, font_id: FreeTypeFontId, string: str, width: int = 0, height: int = 0) -> BBox:
        size_calc = CalculateSize()
        _freetype.render_string(self.ptr, self.caches.bitcache, font_id.id, width, height, string, size_calc.font_callback)
        return BBox(x=size_calc.x, y=size_calc.y)

    def _render_mask(self, dest, size, x, y, fill, f):
        temporary = Image.new("L", (size.x, size.y), 0)
        f(temporary)
        ink, _ = draw._getink(fill)
        _freetype.draw_bitmap((x, y), temporary.im.id, dest.im.id, ink)

    def render(self, font_id: FreeTypeFontId, image: Image, string: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0, fill: Tuple = (255, 255, 255)):
        bounding_box = self.calculate_size(font_id, string, width, height)

        self._render_mask(
            image,
            bounding_box, x, y, fill,
            f=lambda t: _freetype.render_string(self.ptr, self.caches.bitcache, font_id.id, width, height, string, BlitChars(t, 0, bounding_box.y).font_callback)
        )

    def render_stroker(self, font_id: FreeTypeFontId, string: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0, fill: Tuple = (255, 255, 255)):
        bounding_box = self.calculate_size(font_id, string, width, height)

        stroke_width = 2

        self._render_mask(
            image,
            BBox(x=bounding_box.x + (2 * stroke_width), y=bounding_box.y + (2 * stroke_width)), x, y, fill,
            f=lambda t: _freetype.render_string_stroker(self.library.ptr, self.caches.cmapcache, self.caches.imagecache, font_id.id, width, height, string, stroke_width, BlitChars(t, 0, bounding_box.y + stroke_width).font_callback)
        )

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


class CalculateSize:

    def __init__(self):
        self.y = 0
        self.x = 0

    def font_callback(self, width, height, left, top, format, max_grays, pitch, xadvance, yadvance, mv):
        self.x += xadvance
        self.y = max(self.y, height)


class BlitChars:

    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.baseline = y

    def font_callback(self, width, height, left, top, format, max_grays, pitch, xadvance, yadvance, mv):
        _freetype.blit_glyph(self.image.im.id, self.x, self.baseline - top, mv, width, height, pitch)
        self.x += xadvance


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


class DumpMetrics:

    def font_callback(self, *args):
        print(*args)


class Noop:
    def font_callback(self, *args):
        pass


def print_timing(loops, thing):
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

    time_taken = timeit.timeit(thing, number=loops)
    print(f"  {format_time(time_taken)}")
    print(f"  {format_time(time_taken / loops)}")


if __name__ == "__main__":

    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (800, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    renderable = "Date: 2022-09-26 Time: 14:35:26.1"

    rendered = True
    timing = True

    font_size = 50

    pillow_font = font.load_font("Roboto-Medium.ttf", font_size)


    def pillow_stroked():
        draw.text(
            (0, 150),
            renderable,
            anchor="la",
            direction="ltr",
            font=pillow_font,
            fill=(255, 255, 255),
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )

    def pillow_plain():
        draw.text(
            (0, 75),
            renderable,
            anchor="la",
            direction="ltr",
            font=pillow_font,
            fill=(255, 0, 0),
        )


    def new_image_pillow():
        temporary = Image.new("L", (400, 200), 0)
        draw = ImageDraw.Draw(image)
        ink, _ = draw._getink((0, 0, 0))
        draw.draw.draw_bitmap((2, 2), temporary.im, ink)


    def new_image_james():
        temporary = Image.new("L", (400, 200), 0)
        ink, _ = draw._getink((0, 0, 0))
        _freetype.draw_bitmap((2, 2), temporary.im.id, image.im.id, ink)


    pillow_stroked()
    pillow_plain()

    with FreeType() as ft:
        print(ft.version())

        with ft.create_cache() as cache:
            id = cache.register_font("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf")


            def cached_stroked():
                cache.render_stroker(id, renderable, height=font_size, x=10, y=50, fill=(0, 0, 0))
                cache.render(id, string=renderable, image=image, height=font_size, x=12, y=52, fill=(255, 255, 255))

            def cached_plain():
                cache.render(id, string=renderable, image=image, height=font_size, x=12, y=0, fill=(255, 0, 0))

            cached_stroked()
            cached_plain()

            if timing:
                loops = 100
                print("New Image Pillow")
                print_timing(100, new_image_pillow)
                print("New Image james")
                print_timing(100, new_image_james)
                print("Cache - Stroked")
                print_timing(loops, cached_stroked)
                print("Cache - Plain")
                print_timing(loops, cached_plain)
                print("Pillow - Stroked")
                print_timing(loops, pillow_stroked)
                print("Pillow - Plain")
                print_timing(loops, pillow_stroked)

    if rendered:
        image.show()
