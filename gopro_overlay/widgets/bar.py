from PIL import ImageDraw, Image

from .widgets import Widget


class Bar(Widget):

    def __init__(self, size, reading, min_value=-10, max_value=10, cr=5, fill=(255, 255, 255, 0),
                 outline=(255, 255, 255),
                 outline_width=3,
                 highlight_colour_negative=(255, 0, 0),
                 highlight_colour_positive=(0, 255, 0),
                 zero=(255, 255, 255),
                 bar=(255, 255, 255)
                 ):
        self.reading = reading
        self.size = size
        self.corner_radius = cr
        self.outline = outline
        self.fill = fill
        self.highlight_colour_positive = highlight_colour_positive
        self.highlight_colour_negative = highlight_colour_negative
        self.zero = zero
        self.bar = bar

        self.line_width = outline_width
        self.min_value = min_value
        self.max_value = max_value

    def x_coord(self, value):
        value = max(min(value, self.max_value), self.min_value)
        range = self.max_value - self.min_value
        scale = (self.size.x - (self.line_width + 2)) / range
        shifted = value - self.min_value
        return shifted * scale

    def draw(self, image: Image, draw: ImageDraw):
        current = self.reading()
        draw.rounded_rectangle(
            ((0, 0), (self.size.x - 1, self.size.y - 1)),
            radius=self.corner_radius,
            fill=self.fill,
            outline=self.outline,
            width=self.line_width,
        )
        draw.line(
            ((self.x_coord(0), 0), (self.x_coord(0), self.size.y)),
            fill=self.zero
        )
        draw.rectangle(
            ((self.x_coord(current), self.line_width + 1), (self.x_coord(0), self.size.y - (self.line_width + 2))),
            fill=self.bar
        )
        highlight_colour = self.highlight_colour_positive if current >= 0 else self.highlight_colour_negative
        draw.rectangle(
            ((self.x_coord(current * 0.95), self.line_width + 1),
             (self.x_coord(current), self.size.y - (self.line_width + 2))),
            fill=highlight_colour
        )
