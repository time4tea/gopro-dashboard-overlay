from PIL import Image, ImageDraw

from gopro_overlay.widgets_map import draw_marker


class SimpleChart:

    def __init__(self, at, value, font=None, filled=False):
        self.at = at
        self.value = value
        self.filled = filled
        if font:
            self.font = font.font_variant(size=16)
        else:
            self.font = None

        self.view = None
        self.image = None

    def draw(self, i, draw):
        view = self.value()

        if self.view and self.view.version == view.version:
            pass
        else:
            self.view = view
            data = view.data
            size = (len(data), 64)
            self.image = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(self.image)

            max_val = max(filter(None.__ne__, data), default=0)
            min_val = min(filter(None.__ne__, data), default=0)

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
                    draw.line(points, width=1, fill=(91, 113, 146))

            points = [(x, y_pos(y)) for x, y in filtered]
            draw.line(points, width=2, fill=(255, 255, 255))

            if self.font:
                draw.text((10, 4), f"{max_val:.0f}", font=self.font, fill=(255, 255, 255), stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((10, 40), f"{min_val:.0f}", font=self.font, fill=(255, 255, 255), stroke_width=2,
                          stroke_fill=(0, 0, 0))

            marker_val = data[int(size[0] / 2)]
            if marker_val:
                draw_marker(draw, (size[0] / 2, y_pos(marker_val)), 4, fill=(255, 0, 0))

            self.image.putalpha(int(255 * 0.7))

        i.alpha_composite(self.image, self.at.tuple())
