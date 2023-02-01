from functools import cache, cached_property
from PIL import ImageDraw, Image

from .widgets import Widget





class GradientBar(Widget):

    def __init__(self, size, reading, min_value=0, max_value=1000, z1_value=120, z2_value=150, z3_value=180, cr=5, 
                fill=(255, 255, 255, 0),
                 outline=(255, 255, 255),
                 outline_width=3,
                 z0_color=(255,255,255),
                 z1_color=(67, 235, 52),
                 z2_color=(240, 232, 19),
                 z3_color=(207, 19, 2),
                #  highlight_colour_negative=(255, 0, 0),
                #  highlight_colour_positive=(0, 255, 0),
                 divider=(255, 255, 255),
                #  bar=(255, 255, 255)
                 ):
        self.reading = reading
        self.size = size
        self.corner_radius = cr
        self.outline = outline
        self.fill = fill
        # self.highlight_colour_positive = highlight_colour_positive
        # self.highlight_colour_negative = highlight_colour_negative
        self.divider = divider
        # self.bar = bar

        self.line_width = outline_width
        self.min_value = min_value
        self.max_value = max_value
        self.z1_value = z1_value
        self.z2_value = z2_value
        self.z3_value = z3_value
        self.z0_color = z0_color
        self.z1_color = z1_color
        self.z2_color = z2_color
        self.z3_color = z3_color
        # print(self.min_value)

    @cache
    def x_coord(self, value):
        value = max(min(value, self.max_value), self.min_value)
        scale = self.scale
        shifted = value - self.min_value
        return shifted * scale

    @cached_property
    def scale(self):
        range = self.max_value - self.min_value
        scale = (self.size.x - (self.line_width + 2)) / range #px/unit
        return scale

    @cache
    def value(self, x_coord):
        scale = self.scale
        shifted = x_coord / scale
        return shifted + self.min_value

    # @staticmethod
    # def interpolate(f_co, t_co, interval):
    #     det_co =[(t - f) / interval for f , t in zip(f_co, t_co)]
    #     for i in range(interval):
    #         yield [round(f + det * i) for f, det in zip(f_co, det_co)]

    @cache
    def get_color(self, x_coord):
        value = self.value(x_coord)
        # print(f"x={x_coord} value={value}", file=sys.stderr)
        if value < self.z1_value:
            range = self.x_coord(self.z1_value) - self.x_coord(self.min_value)
            i = x_coord - self.x_coord(self.min_value)
            gradient_step = [(t-f)/range for f, t in zip(self.z0_color, self.z1_color)]
            return [round(f + gs * i) for f, gs in zip(self.z0_color, gradient_step)]
        elif value < self.z2_value:
            range = self.x_coord(self.z2_value) - self.x_coord(self.z1_value)
            i = x_coord - self.x_coord(self.z1_value)
            gradient_step = [(t-f)/range for f, t in zip(self.z1_color, self.z2_color)]
            return [round(f + gs * i) for f, gs in zip(self.z1_color, gradient_step)]
        elif value < self.z3_value:
            range = self.x_coord(self.z3_value) - self.x_coord(self.z2_value)
            i = x_coord - self.x_coord(self.z2_value)
            gradient_step = [(t-f)/range for f, t in zip(self.z2_color, self.z3_color)]
            return [round(f + gs * i) for f, gs in zip(self.z2_color, gradient_step)]
        else:
            return self.z3_color

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
            fill=self.divider
        )
        for i in range(round(self.x_coord(0))+self.line_width, round(self.x_coord(current))):
            draw.line(((i, self.line_width), (i, self.size.y-self.line_width-1)), tuple(self.get_color(i)), width=1)
        if self.divider:
            for v in (self.z1_value, self.z2_value, self.z3_value):
                draw.line(
                    ((self.x_coord(v), self.line_width), (self.x_coord(v), self.size.y-self.line_width-1)),
                    fill=self.divider
                )
        # draw.rectangle(
        #     ((self.x_coord(current), self.line_width + 1), (self.x_coord(0), self.size.y - (self.line_width + 2))),
        #     fill=self.bar
        # )
        # highlight_colour = self.highlight_colour_positive if current >= 0 else self.highlight_colour_negative
        # draw.rectangle(
        #     ((self.x_coord(current * 0.95), self.line_width + 1),
        #      (self.x_coord(current), self.size.y - (self.line_width + 2))),
        #     fill=highlight_colour
        # )
