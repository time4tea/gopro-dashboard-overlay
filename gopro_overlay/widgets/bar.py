from PIL import ImageDraw, Image

from .widgets import Widget


class Bar(Widget):

    def __init__(self, size, reading, min_value=-10, max_value=10, cr=5, fill=(255, 255, 255, 0),
                 outline=(255, 255, 255),
                 outline_width=3,
                 highlight_colour_negative=(255, 0, 0),
                 highlight_colour_positive=(0, 255, 0),
                 zero=(255, 255, 255),
                 bar=(255, 255, 255),
                 align_center=False
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
        self.align_center = align_center

        self.line_width = outline_width
        self.min_value = min_value
        self.max_value = max_value

        self.solid = lambda colors: any(len(color) != 4 or color[3] != 0 for color in colors)
        self.test_solid = lambda solid, transparent, color: solid if self.solid((color,)) else transparent

    def x_coord(self, value):
        value = max(min(value, self.max_value), self.min_value)
        range = self.max_value - self.min_value
        scale = (self.size.x - self.test_solid(self.line_width + 2, 0, self.outline)) / range
        shifted = value - self.min_value
        return shifted * scale

    def draw(self, image: Image, draw: ImageDraw):
        # Don't draw transparent colours to allow for overlaying
        
        current = self.reading()
        if self.solid((self.fill, self.outline)):
            draw.rounded_rectangle(
                ((0, 0), (self.size.x - 1, self.size.y - 1)),
                radius=self.corner_radius,
                fill=self.fill,
                outline=self.outline,
                width=self.line_width,
            )
        if self.solid((self.zero,)):
            draw.line(
                ((self.x_coord(0), 0), (self.x_coord(0), self.size.y)),
                fill=self.zero
            )

        if self.align_center:
            if current == self.min_value:
                return # Bypass rounding error by not drawing anything
            start_x = self.size.x / 2 - self.x_coord(current) / 2
            end_x = self.size.x / 2 + self.x_coord(current) / 2

            draw.rectangle(
                ((start_x, self.test_solid(self.line_width + 1, 0, self.outline)), (end_x, self.size.y - self.test_solid(self.line_width + 2, 0, self.outline))),
                fill=self.bar
            )
            return

        if current >= 0:
            start_x = self.x_coord(0)
            end_x = self.x_coord(current)

            start_hx = self.x_coord(current * 0.95)

            draw.rectangle(
                ((start_x, self.line_width + 1), (end_x, self.size.y - (self.line_width + 2))),
                fill=self.bar
            )

            draw.rectangle(
                ((start_hx, self.line_width + 1),
                 (end_x, self.size.y - (self.line_width + 2))),
                fill=self.highlight_colour_positive
            )

        else:
            start_x = self.x_coord(current)
            end_x = self.x_coord(0)

            start_hx = self.x_coord(current * 0.95)

            draw.rectangle(
                ((start_x, self.line_width + 1), (end_x, self.size.y - (self.line_width + 2))),
                fill=self.bar
            )

            draw.rectangle(
                ((start_x, self.line_width + 1),
                 (start_hx, self.size.y - (self.line_width + 2))),
                fill=self.highlight_colour_negative
            )
