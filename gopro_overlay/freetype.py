import _freetype


class FreeTypeFontSize:

    def __init__(self, ptr):
        # ptr = FT_SizeRec
        self.ptr = ptr

    def render(self, string: str):
        _freetype.render_render_string(self.ptr, string)

    def __str__(self) -> str:
        return f"SizeRec: {self.ptr}"


class FreeTypeCacheManager:

    def __init__(self, library):
        # ptr = FTC_Manager
        self.ptr = _freetype.cache_manager_new(library.ptr, self._id_to_path)
        self.known = {}
        self.counter = 0

    def _id_to_path(self, id):
        path = self.known[id]
        print(f"Returning {path}")
        return path

    def get_font_with_size(self, path, width=0, height=0):
        if path in self.known:
            id = self.known[path]
        else:
            self.counter += 1
            id = self.counter
            self.known[id] = path

        return FreeTypeFontSize(_freetype.cache_manager_get_face(self.ptr, id, width, height))

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
    with FreeType() as ft:
        print(ft.version())

        with ft.create_cache() as cache:
            size = cache.get_font_with_size("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf", height=10)
            print(size)
            size.render("Hello")
            size.render("World")
