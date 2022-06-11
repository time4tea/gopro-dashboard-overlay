import functools

from PIL import Image, ImageDraw

from gopro_overlay.widgets_compass import Compass


class CompassArrow:

    def __init__(self, size, reading, font,
                 arrow=(255, 255, 255),
                 bg=(0, 0, 0, 0),
                 text=(255, 255, 255),
                 outline=(0, 0, 0),
                 arrow_outline=(0, 0, 0)
                 ):
        self.reading = reading
        self.size = size
        self.font = font
        self.arrow = arrow
        self.arrow_outline = arrow_outline
        self.bg = bg
        self.text = text
        self.outline = outline
        self.last_reading = None
        self.image = None

    def _redraw(self, reading):
        size = self.size
        image = Image.new(mode="RGBA", size=(size, size))

        draw = ImageDraw.Draw(image)

        draw.pieslice(
            ((0, 0), (0 + size, 0 + size)),
            0,
            360,
            outline=self.outline,
            fill=self.bg,
            width=2
        )

        radius = size / 2
        centre = size / 2

        locate = functools.partial(Compass.locate, radius, centre, 0)

        draw.text(locate(0, radius * 0.3), "N", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(90, radius * 0.3), "E", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(180, radius * 0.3), "S", font=self.font, anchor="mm", fill=self.text)
        draw.text(locate(270, radius * 0.3), "W", font=self.font, anchor="mm", fill=self.text)

        locate = functools.partial(Compass.locate, radius, centre, -reading)

        draw.polygon(
            [
                locate(0, radius * 0.45),
                locate(-90, (radius * 0.9)),
                locate(0, (radius * 0.9)),
                locate(90, (radius * 0.9)),
            ],
            fill=self.arrow,
            outline=self.arrow_outline,
        )

        return image

    def draw(self, image, draw):
        reading = - int(self.reading())

        if self.image is None or reading != self.last_reading:
            self.last_reading = reading
            self.image = self._redraw(reading)

        image.alpha_composite(self.image, (0, 0))
