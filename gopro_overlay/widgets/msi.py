from typing import Callable

from PIL import Image, ImageDraw

from .asi import roundup, scale, Arc
from .widgets import Widget


class MotorspeedIndicator(Widget):

    def __init__(self, size: int, font, needle: bool, reading: Callable[[], float], green: int, yellow: int, end: int,
                 rotate: int = 180, outline: int = 2):
        self.end = end
        self.yellow = yellow
        self.green = green
        self.font = font
        self.needle = needle
        self.reading = reading
        self.outline = outline

        self.width = int(size / 17)

        self.step = 5

        self.asi_max = roundup(end * 0.05 + end, self.step * 4)

        self.size = size
        self.bg = None
        self.fg = (255, 255, 255)
        self.text = (255, 255, 255)

        self.xa = scale(0, self.asi_max, rotate)

        self.image = None

    def ticklenwidth(self, value):
        if value % 10 == 0:
            return int(self.width) + int(self.size / 51), int(self.size / 128)
        return int(self.width) - int(self.size / 51), int(self.size / 256)

    def draw_msi(self):

        image = Image.new(mode="RGBA", size=(self.size, self.size))
        draw = ImageDraw.Draw(image)

        widths = self.width

        arc = Arc(self.size)

        arc.pieslice(draw, 0, outline=(0, 0, 0, 128), fill=(0, 0, 0, 128), width=int(self.size / 128))

        if self.needle:
            arc.arc(draw, 0, start=self.xa(self.green), end=self.xa(self.yellow), fill=(51, 193, 25), width=widths)
            arc.arc(draw, 0, start=self.xa(self.yellow), end=self.xa(self.end), fill=(237, 239, 42), width=widths)

            for value in range(0, self.asi_max + self.step, self.step):
                ticklen, width = self.ticklenwidth(value)
                arc.line(draw, [(self.xa(value), ticklen), (self.xa(value), 0)], fill=self.fg, width=width)

        for value in range(0, self.asi_max + (self.step * 4), self.step * 4):
            draw.text(
                arc.locate(self.xa(value), int(self.size / 6.5)),
                str(value),
                font=self.font,
                anchor="mm",
                fill=self.text,
                stroke_width=self.outline,
                stroke_fill=(0, 0, 0)
            )

        return image

    def draw(self, image: Image, draw: ImageDraw):

        if self.image is None:
            self.image = self.draw_msi()

        image.alpha_composite(self.image, (0, 0))

        reading = self.reading()
        color = (0, 191, 255)

        if reading < 0:
            reading = 0
        # Possible change color according ranges
        # elif reading < 50:
        #    color = (51, 193, 25)
        # elif reading < 180:
        #    color = (237, 239, 42)

        arc = Arc(self.size)

        if self.needle:  # Needle
            draw.polygon(
                [
                    arc.locate(self.xa(reading) - 0, 0),
                    arc.locate(self.xa(reading) - 90, (self.size / 2) - (self.size / 32)),
                    arc.locate(self.xa(reading) - 180, (self.size / 2) - (self.size / 32)),
                    arc.locate(self.xa(reading) + 90, (self.size / 2) - (self.size / 32)),
                ],
                fill=self.fg
            )
        else:  # Arc
            arc.arc(draw, 0, start=self.xa(0), end=self.xa(reading), fill=color, width=self.width)

            # Marker
            # radius = int(self.size/9) #27
            # x0 = arc.centre + ((arc.centre - radius) * math.sin(math.radians(self.xa(reading)))) - self.width/2
            # y0 = arc.centre - ((arc.centre - radius) * math.cos(math.radians(self.xa(reading)))) - self.width/2
            # x1 = arc.centre + ((arc.centre - radius) * math.sin(math.radians(self.xa(reading)))) + self.width/2
            # y1 = arc.centre - ((arc.centre - radius) * math.cos(math.radians(self.xa(reading)))) + self.width/2
            # draw.ellipse([(x0,y0),(x1,y1)],fill ="#ADD8E6", outline ="#ADD8E6")

            for value in range(0, self.asi_max + self.step, self.step):
                ticklen, width = self.ticklenwidth(value)
                arc.line(draw, [(self.xa(value), ticklen), (self.xa(value), 0)], fill=self.fg, width=width)


class MotorspeedIndicator2(Widget):

    def __init__(self, size: int, font, reading: Callable[[], float], green: int, yellow: int, end: int,
                 rotate: int = 180, outline: int = 2):
        self.end = end
        self.yellow = yellow
        self.green = green
        self.font = font
        self.reading = reading
        self.outline = outline

        self.width = int(size / 17)
        self.offset = int(size / 51)

        self.step = 5

        self.asi_max = roundup(end * 0.05 + end, self.step * 4)

        self.size = size
        self.bg = None
        self.fg = (255, 255, 255)
        self.text = (255, 255, 255)

        self.xa = scale(0, self.asi_max, rotate)

        self.image = None

    def ticklenwidth(self, value):
        if value % 10 == 0:
            return int(self.width * 2) + self.offset - 2, int(self.size / 128)
        return int(self.width) + self.offset, int(self.size / 256)

    def draw_msi(self):

        image = Image.new(mode="RGBA", size=(self.size, self.size))
        draw = ImageDraw.Draw(image)

        widths = self.width

        arc = Arc(self.size)

        arc.pieslice(draw, 0, outline=(0, 0, 0, 128), fill=(0, 0, 0, 128), width=int(self.size / 128))
        arc.arc(draw, self.offset, start=self.xa(self.green), end=self.xa(self.yellow), fill=(51, 193, 25),
                width=widths)
        arc.arc(draw, self.offset, start=self.xa(self.yellow), end=self.xa(self.end), fill=(237, 239, 42), width=widths)

        for value in range(0, self.asi_max + (self.step * 4), self.step * 4):
            draw.text(
                arc.locate(self.xa(value), int(self.size / 4.5)),
                str(value),
                font=self.font,
                anchor="mm",
                fill=self.text,
                stroke_width=self.outline,
                stroke_fill=(0, 0, 0)
            )

        return image

    def draw(self, image: Image, draw: ImageDraw):

        if self.image is None:
            self.image = self.draw_msi()

        image.alpha_composite(self.image, (0, 0))

        reading = self.reading()

        if reading < 0:
            reading = 0

        arc = Arc(self.size)
        arc.arc(draw, self.offset + self.width, start=self.xa(0), end=self.xa(reading), fill=(0, 191, 255),
                width=self.width)

        # Marker
        # radius = int(self.size/9) #27
        # x0 = arc.centre + ((arc.centre - radius) * math.sin(math.radians(self.xa(reading)))) - self.width/2
        # y0 = arc.centre - ((arc.centre - radius) * math.cos(math.radians(self.xa(reading)))) - self.width/2
        # x1 = arc.centre + ((arc.centre - radius) * math.sin(math.radians(self.xa(reading)))) + self.width/2
        # y1 = arc.centre - ((arc.centre - radius) * math.cos(math.radians(self.xa(reading)))) + self.width/2
        # draw.ellipse([(x0,y0),(x1,y1)],fill ="#ADD8E6", outline ="#ADD8E6")

        for value in range(0, self.asi_max + self.step, self.step):
            ticklen, width = self.ticklenwidth(value)
            arc.line(draw, [(self.xa(value), ticklen), (self.xa(value), 0)], fill=self.fg, width=width)
