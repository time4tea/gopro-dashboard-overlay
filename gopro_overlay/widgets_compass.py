import functools
import math

from PIL import Image, ImageDraw


class Compass:

    def __init__(self, size, reading, font, fg=(255, 255, 255), bg=(0, 0, 0), text=(255, 255, 255)):
        self.reading = reading
        self.size = size
        self.font = font
        self.fg = fg
        self.bg = bg
        self.text = text
        self.last_reading = None
        self.image = None

    @staticmethod
    def locate(centre, radius, reading, angle, d):
        return (
            centre + ((radius - d) * math.sin(math.radians(angle + reading))),
            centre - ((radius - d) * math.cos(math.radians(angle + reading)))
        )

    def _redraw(self, reading):

        size = self.size * 2
        image = Image.new(mode="RGBA", size=(size, size))
        draw = ImageDraw.Draw(image)

        centre = size / 2
        radius = size / 2

        major_tick = size / 7
        minor_tick = size / 10
        tiny_tick = size / 20
        teeny_tick = size / 30

        locate = functools.partial(Compass.locate, centre, radius, reading)

        draw.pieslice(
            ((0, 0), (0 + size, 0 + size)),
            0,
            360,
            outline=self.fg,
            fill=self.bg,
            width=2
        )

        draw.arc(
            ((0 + size * 0.35, 0 + size * 0.35), (0 + size * 0.65, 0 + size * 0.65)),
            0,
            360,
            width=2,
            fill=self.fg
        )

        draw.point((centre, centre), fill=self.fg)

        def ticklen(angle):
            if angle % 90 == 0:
                return major_tick
            elif angle % 45 == 0:
                return minor_tick
            elif angle % 10 == 0:
                return tiny_tick
            else:
                return teeny_tick

        for angle in range(0, 360, 5):
            tick_len = ticklen(angle)
            draw.line([
                locate(angle, tick_len),
                locate(angle, 0)
            ],
                fill=self.fg,
                width=2,
            )

        draw.polygon(
            [
                locate(0, 0),
                locate(- 5, minor_tick),
                locate(5, minor_tick),
            ],
            fill=self.fg
        )

        draw.polygon(
            [
                locate(-reading - 0, 0),
                locate(-reading - 5, tiny_tick),
                locate(-reading + 5, tiny_tick),
            ],
            fill=self.fg
        )

        actual = image.resize((self.size, self.size), Image.BILINEAR)

        locate = functools.partial(Compass.locate, self.size / 2, self.size / 2, reading)

        draw = ImageDraw.Draw(actual)
        draw.text(locate(0, self.size / 4), "N", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(90, self.size / 4), "E", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(180, self.size / 4), "S", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(270, self.size / 4), "W", font=self.font, anchor="mm", fill=self.text)

        draw.point((self.size / 2, self.size / 2), fill=self.fg)

        return actual

    def draw(self, image, draw):
        reading = - int(self.reading())

        if self.image is None or reading != self.last_reading:
            self.last_reading = reading
            self.image = self._redraw(reading)

        image.alpha_composite(self.image, (0, 0))
