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

    def _redraw(self, reading):

        image = Image.new(mode="RGBA", size=(self.size, self.size))
        draw = ImageDraw.Draw(image)

        centre = self.size / 2
        radius = self.size / 2

        major_tick = self.size / 7
        minor_tick = self.size / 10
        tiny_tick = self.size / 20
        teeny_tick = self.size / 30

        def locate(angle, d):
            return (
                centre + ((radius - d) * math.sin(math.radians(angle + reading))),
                centre - ((radius - d) * math.cos(math.radians(angle + reading)))
            )

        draw.pieslice(
            ((0, 0), (0 + self.size, 0 + self.size)),
            0,
            360,
            outline=self.fg,
            fill=self.bg,
            width=2
        )

        draw.arc(
            ((0 + self.size * 0.35, 0 + self.size * 0.35), (0 + self.size * 0.65, 0 + self.size * 0.65)),
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

        draw.text(locate(0, major_tick * 1.5), "N", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(90, major_tick * 1.5), "E", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(180, major_tick * 1.5), "S", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(270, major_tick * 1.5), "W", font=self.font, anchor="mm", fill=self.text)

        return image

    def draw(self, image, draw):
        reading = - int(self.reading())

        if self.image is None or reading != self.last_reading:
            self.last_reading = reading
            self.image = self._redraw(reading)

        image.alpha_composite(self.image, (0, 0))
