import cairo


class FontFace:

    def text_extents(self, context: cairo.Context, text: str) -> cairo.TextExtents:
        raise NotImplementedError()

    def show(self, context: cairo.Context, text: str):
        raise NotImplementedError()


class PangoFontFace(FontFace):
    pass


class ToyFontFace(FontFace):

    def __init__(self, family: str, slant: cairo.FontSlant = cairo.FONT_SLANT_NORMAL,
                 weight: cairo.FontWeight = cairo.FONT_WEIGHT_NORMAL):
        self.face = cairo.ToyFontFace(family, slant, weight)

    def text_extents(self, context: cairo.Context, text: str) -> cairo.TextExtents:
        context.set_font_face(self.face)
        return context.text_extents(text)

    def show(self, context: cairo.Context, text: str):
        context.set_font_face(self.face)
        context.show_text(text)
