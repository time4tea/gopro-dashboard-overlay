import dbm.ndbm
from functools import partial
from pathlib import Path

import geotiler
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

        map = geotiler.Map(center=(-0.1499, +51.4972), zoom=19, size=(256, 256))
        image = render(map)

        print(map.extent)

        image.show()
