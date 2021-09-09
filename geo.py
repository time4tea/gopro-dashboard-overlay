import dbm.ndbm
import math
from functools import partial
from pathlib import Path

import geotiler
from PIL import ImageDraw
from geotiler.cache import caching_downloader
from geotiler.tile.io import fetch_tiles


def dbm_downloader(dbm_file):
    get = lambda key: dbm_file.get(key, None)
    set = lambda key, value: dbm_file.setdefault(key, value)

    return partial(caching_downloader, get, set, fetch_tiles)


def dbm_caching_renderer(dbm_file):
    return partial(geotiler.render_map, downloader=dbm_downloader(dbm_file))


if __name__ == "__main__":
    ourdir = Path.home().joinpath(".gopro-graphics")
    ourdir.mkdir(exist_ok=True)

    with dbm.ndbm.open(str(ourdir.joinpath("tilecache.ndbm")), "c") as db:
        render = dbm_caching_renderer(db)

        desired = 256
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
