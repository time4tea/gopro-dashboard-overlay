import math
import os

import geotiler
from PIL import ImageDraw

from gopro_overlay.geo import CachingRenderer

if __name__ == "__main__":

    api_key = os.environ["API_KEY"]

    with CachingRenderer(
        style="tf-pioneer", api_key=api_key
    ).open() as render:
        desired = 512
        hyp = int(math.sqrt((desired ** 2) * 2))

        print(f"desired = {desired}, hyp={hyp}")

        bounds = (
            (hyp / 2) - (desired / 2),
            (hyp / 2) - (desired / 2),
            (hyp / 2) + (desired / 2),
            (hyp / 2) + (desired / 2)
        )

        map = geotiler.Map(center=(-0.1499, +51.4972), zoom=19, size=(hyp, hyp))
        orig = render(map)
        draw = ImageDraw.Draw(orig)
        draw.ellipse((
            (hyp / 2) - 3,
            (hyp / 2) - 3,
            (hyp / 2) + 3,
            (hyp / 2) + 3
        ), fill=(255, 0, 0), outline=(0, 0, 0)
        )

        for rot in range(0, 360, 360):
            image = orig.rotate(rot).crop(bounds)
            image.show()
