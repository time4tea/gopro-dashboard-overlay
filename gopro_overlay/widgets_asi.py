import math

from PIL import Image, ImageDraw


def roundup(x, n=10):
    return int(math.ceil(x / n)) * n


class AirspeedIndicator:
    """Modelled on https://aerotoolbox.com/airspeed-indicator/"""

    def __init__(self, size, font, reading, Vs0, Vs, Vfe, Vn0, Vne):
        self.Vne = Vne
        self.Vn0 = Vn0
        self.Vfe = Vfe
        self.Vs = Vs
        self.Vs0 = Vs0
        self.font = font
        self.reading = reading

        self.step = 5

        self.asi_max = roundup((Vne - Vs0) * 0.20 + Vne, self.step * 4)

        self.range = self.asi_max - Vs0

        self.size = size
        self.bg = None
        self.fg = (255, 255, 255)
        self.text = (255, 255, 255)


        self.image = None

    def xa(self, value, arc=True):
        start_angle = 30
        end_angle = 360 - start_angle

        a_range = end_angle - start_angle
        v_point = (value - self.Vs0) / self.range

        a_point = a_range * v_point

        correction = 90 if arc else 0

        return a_point + start_angle - correction

    def locate(self, angle, d):

        centre = self.size / 2
        radius = self.size / 2

        return (
            centre + ((radius - d) * math.sin(math.radians(angle))),
            centre - ((radius - d) * math.cos(math.radians(angle)))
        )

    def draw_asi(self):

        image = Image.new(mode="RGBA", size=(self.size, self.size))
        draw = ImageDraw.Draw(image)

        widths = 15

        def ticklenwidth(value):
            if value % 10 == 0:
                return 33, 2
            return 27, 1

        draw.pieslice(
            ((0, 0), (0 + self.size, 0 + self.size)),
            0,
            360,
            outline=(0, 0, 0, 128),
            fill=(0, 0, 0, 128),
            width=2
        )

        offset = 5
        draw.arc(
            ((offset, offset), (0 + self.size - offset, 0 + self.size - offset)),
            self.xa(self.Vs0),
            self.xa(self.Vfe),
            fill=self.fg,
            width=widths
        )

        draw.arc(
            (
                (widths + offset, widths + offset),
                (0 + self.size - (widths + offset), 0 + self.size - (widths + offset))),
            self.xa(self.Vs),
            self.xa(self.Vn0),
            fill=(51, 193, 25),
            width=widths
        )

        draw.arc(
            (
                (widths + offset, widths + offset),
                (0 + self.size - (widths + offset), 0 + self.size - (widths + offset))),
            self.xa(self.Vn0),
            self.xa(self.Vne),
            fill=(237, 239, 42),
            width=widths
        )

        draw.line([
            self.locate(self.xa(self.Vne, arc=False), 40),
            self.locate(self.xa(self.Vne, arc=False), 0)
        ],
            fill=(246, 34, 21),
            width=5,
        )

        for value in range(self.Vs0, self.asi_max + self.step, self.step):
            ticklen, width = ticklenwidth(value)
            draw.line([
                self.locate(self.xa(value, arc=False), ticklen),
                self.locate(self.xa(value, arc=False), 0)
            ],
                fill=self.fg,
                width=width,
            )

        for value in range(self.Vs0, self.asi_max + (self.step * 4), self.step * 4):
            draw.text(
                self.locate(self.xa(value, arc=False), int(self.size / 4.5)),
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

        draw.polygon(
            [
                self.locate(self.xa(reading, arc=False) - 0, 0),
                self.locate(self.xa(reading, arc=False) - 90, (self.size / 2) - 8),
                self.locate(self.xa(reading, arc=False) - 180, (self.size / 2) - 8),
                self.locate(self.xa(reading, arc=False) + 90, (self.size / 2) - 8),
            ],
            fill=self.fg
        )
