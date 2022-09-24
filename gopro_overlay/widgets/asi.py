import math

from PIL import Image, ImageDraw


def roundup(x, n=10):
    return int(math.ceil(x / n)) * n


class Arc:
    def __init__(self, size):
        self.centre = size / 2
        self.correction = 90

    def bbox(self, r_delta):
        return (
            (self.centre - (self.centre - r_delta), self.centre - (self.centre - r_delta)),
            (self.centre + (self.centre - r_delta), self.centre + (self.centre - r_delta))
        )

    def arc(self, draw, r_delta, start=0, end=360, **kwargs):
        draw.arc(
            self.bbox(r_delta),
            start=start - self.correction,
            end=end - self.correction,
            **kwargs
        )

    def pieslice(self, draw, r_delta, start=0, end=360, **kwargs):
        draw.pieslice(
            self.bbox(r_delta),
            start=start - self.correction,
            end=end - self.correction,
            **kwargs
        )

    def locate(self, angle, r_delta):
        return (
            self.centre + ((self.centre - r_delta) * math.sin(math.radians(angle))),
            self.centre - ((self.centre - r_delta) * math.cos(math.radians(angle)))
        )

    def line(self, draw, places, **kwargs):
        draw.line(
            [self.locate(a, d) for a, d in places],
            **kwargs
        )


def scale(min_value, max_value, rotate=0):
    start_angle = 30
    end_angle = 360 - start_angle

    a_range = end_angle - start_angle

    def s(v):
        v_point = (v - min_value) / (max_value - min_value)

        a_point = a_range * v_point

        return a_point + start_angle + rotate

    return s


class AirspeedIndicator:
    """Modelled on https://aerotoolbox.com/airspeed-indicator/"""

    def __init__(self, size, font, reading, Vs0, Vs, Vfe, Vno, Vne, rotate=0):
        self.Vne = Vne
        self.Vno = Vno
        self.Vfe = Vfe
        self.Vs = Vs
        self.Vs0 = Vs0
        self.font = font
        self.reading = reading

        self.step = 5

        self.asi_max = roundup((Vne - Vs0) * 0.05 + Vne, self.step * 4)

        self.size = size
        self.bg = None
        self.fg = (255, 255, 255)
        self.text = (255, 255, 255)

        self.xa = scale(self.Vs0, self.asi_max, rotate)

        self.image = None

    def draw_asi(self):

        image = Image.new(mode="RGBA", size=(self.size, self.size))
        draw = ImageDraw.Draw(image)

        widths = 15

        def ticklenwidth(value):
            if value % 10 == 0:
                return 33, 2
            return 27, 1

        arc = Arc(self.size)

        offset = 5

        arc.pieslice(draw, 0, outline=(0, 0, 0, 128), fill=(0, 0, 0, 128), width=2)
        arc.arc(draw, offset, start=self.xa(self.Vs0), end=self.xa(self.Vfe), fill=self.fg, width=widths)
        arc.arc(draw, offset + widths, start=self.xa(self.Vs), end=self.xa(self.Vno), fill=(51, 193, 25), width=widths)
        arc.arc(draw, offset + widths, start=self.xa(self.Vno), end=self.xa(self.Vne), fill=(237, 239, 42),
                width=widths)

        arc.line(draw, [(self.xa(self.Vne), 40), (self.xa(self.Vne), 0)], fill=(246, 34, 21), width=5)

        for value in range(self.Vs0, self.asi_max + self.step, self.step):
            ticklen, width = ticklenwidth(value)
            arc.line(draw, [(self.xa(value), ticklen), (self.xa(value), 0)], fill=self.fg, width=width)

        for value in range(self.Vs0, self.asi_max + (self.step * 4), self.step * 4):
            draw.text(
                arc.locate(self.xa(value), int(self.size / 4.5)),
                str(value),
                font=self.font,
                anchor="mm",
                fill=self.text
            )

        return image

    def draw(self, image, draw):

        if self.image is None:
            self.image = self.draw_asi()

        image.alpha_composite(self.image, (0, 0))

        reading = self.reading()

        if reading < self.Vs0:
            reading = self.Vs0 - 1

        if reading < 0:
            reading = 0

        arc = Arc(self.size)

        draw.polygon(
            [
                arc.locate(self.xa(reading) - 0, 0),
                arc.locate(self.xa(reading) - 90, (self.size / 2) - 8),
                arc.locate(self.xa(reading) - 180, (self.size / 2) - 8),
                arc.locate(self.xa(reading) + 90, (self.size / 2) - 8),
            ],
            fill=self.fg
        )
