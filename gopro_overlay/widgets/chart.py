from PIL import Image, ImageDraw

from .map import draw_marker
from .widgets import Widget


class SimpleChart(Widget):

    def __init__(
            self,
            value,
            font=None,
            filled=False,
            height=64,
            bg=(0, 0, 0, 170),
            fill=(91, 113, 146),
            line=(255, 255, 255),
            text=(255, 255, 255),
    ):
        self.value = value
        self.filled = filled
        self.font = font

        self.height = height
        self.fill = fill
        self.bg = bg
        self.line = line
        self.text = text

        self.view = None
        self.image = None

    def draw(self, image: Image, draw: ImageDraw):
        view = self.value()

        if self.view and self.view.version == view.version:
            pass
        else:
            self.view = view
            data = view.data
            size = (len(data), self.height)
            self.image = Image.new("RGBA", size, self.bg)
            draw = ImageDraw.Draw(self.image)

            values = [i for i in data if i is not None]
            max_val = max(values, default=0)
            min_val = min(values, default=0)

            range_val = max_val - min_val

            if range_val == 0:
                range_val = 1

            scale_y = size[1] / (range_val * 1.1)

            def y_pos(val):
                return size[1] - 1 - (val - min_val) * scale_y

            filtered = [(x, y) for x, y in enumerate(data) if y is not None]

            if self.filled:
                for x, y in filtered:
                    # (0,0) is top left
                    points = ((x, size[1] - 1), (x, y_pos(y)))

                    draw.line(points, width=1, fill=self.fill)

            points = [(x, y_pos(y)) for x, y in filtered]

            draw.line(points, width=2, fill=self.line)

            if self.font:
                draw.text((10, 4), f"{max_val:.0f}", font=self.font, fill=self.text, stroke_width=2,
                          stroke_fill=(0, 0, 0), anchor="lt")
                draw.text((10, self.height - 10), f"{min_val:.0f}", font=self.font, fill=self.text, stroke_width=2,
                          stroke_fill=(0, 0, 0), anchor="lb")

            marker_val = data[int(size[0] / 2)]
            if marker_val:
                draw_marker(draw, (size[0] / 2, y_pos(marker_val)), 4, fill=(255, 0, 0))

        image.alpha_composite(self.image, (0, 0))
