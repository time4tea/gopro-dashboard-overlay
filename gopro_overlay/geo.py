import contextlib
import dbm.ndbm
import itertools
from functools import partial
from pathlib import Path

import geotiler
from geotiler.cache import caching_downloader
from geotiler.provider import MapProvider
from geotiler.tile.io import fetch_tiles

# most of the "stamen" maps in geotiler don't seem to work.
map_styles = list(itertools.chain(
    ["osm"],
    [f"tf-{style}" for style in [
        "cycle", "transport", "landscape",
        "outdoors", "transport-dark", "spinal-map",
        "pioneer", "mobile-atlas", "neighbourhood",
        "atlas"]
     ]
))


def thunderforest_attrs(style):
    return {
        "name": "ThunderForest Map",
        "attribution": "Maps © Thunderforest\nhttp://www.thunderforest.com/\nData © OpenStreetMap contributors\nhttp://www.openstreetmap.org/copyright",
        "url": "https://{subdomain}.tile.thunderforest.com/$MAPSTYLE$/{z}/{x}/{y}.{ext}?apikey={api_key}".replace(
            "$MAPSTYLE$", style),
        "subdomains": ["a", "b", "c"],
        "api-key-ref": "thunderforest",
        "limit": 2,
    }


def provider_for_style(name, api_key):
    if name == "osm":
        return geotiler.find_provider("osm")
    elif name.startswith("tf"):
        style = name.split("-")[1]
        return MapProvider(thunderforest_attrs(style), api_key)
    else:
        raise KeyError(f"Unknown map provider: {name}")


def dbm_downloader(dbm_file):
    get = lambda key: dbm_file.get(key, None)

    def set(key, value):
        if value:
            dbm_file.setdefault(key, value)

    return partial(caching_downloader, get, set, fetch_tiles)


def dbm_caching_renderer(provider, dbm_file):
    def render(map, tiles=None, **kwargs):
        map.provider = provider
        return geotiler.render_map(map, tiles, downloader=dbm_downloader(dbm_file), **kwargs)

    return render


class CachingRenderer:

    def __init__(self, style="osm", api_key=None):
        self.ourdir = Path.home().joinpath(".gopro-graphics")
        self.provider = provider_for_style(style, api_key)

    @contextlib.contextmanager
    def open(self):
        self.ourdir.mkdir(exist_ok=True)

        with dbm.ndbm.open(str(self.ourdir.joinpath("tilecache.ndbm")), "c") as db:
            yield dbm_caching_renderer(self.provider, db)
