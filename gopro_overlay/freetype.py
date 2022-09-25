import _freetype


class FreeType:

    def __init__(self):
        self.ptr = _freetype.freetype_init()

    def version(self):
        return _freetype.freetype_version(self.ptr)

    def __enter__(self):
        if self.ptr is None:
            raise AssertionError("No handle")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _freetype.freetype_done(self.ptr)
        self.ptr = None


if __name__ == "__main__":
    with FreeType() as ft:
        print(hex(ft.ptr))

        print(ft.version())
