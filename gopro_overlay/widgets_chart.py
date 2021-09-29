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

    def draw(self, i, draw):
        data = self.value()

        size = (len(data), 64)
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        max_val = max(filter(None.__ne__, data))
        min_val = min(filter(None.__ne__, data))

        range_val = max_val - min_val

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

        draw_marker(draw, (size[0] / 2, y_pos(data[int(size[0] / 2)])), 4, fill=(255, 0, 0))

        image.putalpha(int(255 * 0.7))
        i.alpha_composite(image, self.at.tuple())
