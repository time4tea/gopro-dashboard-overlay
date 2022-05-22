import contextlib
import dbm.ndbm
import itertools
import json
import os
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
     ],
    [f"geo-{style}" for style in [
        "osm-carto", "osm-bright", "osm-bright-grey", "osm-bright-smooth",
        "klokantech-basic", "osm-liberty", "maptiler-3d", "toner", "toner-grey", "positron",
        "positron-blue", "positron-red", "dark-matter", "dark-matter-brown", "dark-matter-dark-grey",
        "dark-matter-dark-purple", "dark-matter-purple-roads", "dark-matter-yellow-roads"
    ]],
))


def osm_attrs():
    return {
        "name": "OpenStreetMap",
        "attribution": "© OpenStreetMap contributors\nhttp://www.openstreetmap.org/copyright",
        "url": "http://{subdomain}.tile.openstreetmap.org/{z}/{x}/{y}.{ext}",
        "subdomains": ["a", "b", "c"],
        "limit": 2
    }


def geoapify_attrs(style):
    return {
        "name": "Geoapify Map",
        "attribution": "Maps © Geoapify\nhttps://www.geoapify.com/\nData © OpenStreetMap "
                       "contributors\nhttp://www.openstreetmap.org/copyright",
        "url": "https://maps.geoapify.com/v1/tile/$MAPSTYLE$/{z}/{x}/{y}.png?apiKey={api_key}".replace(
            "$MAPSTYLE$", style),
        "api-key-ref": "geoapify",
        "limit": 2,
    }


def thunderforest_attrs(style):
    return {
        "name": "Thunderforest Map",
        "attribution": "Maps © Thunderforest\nhttp://www.thunderforest.com/\nData © OpenStreetMap "
                       "contributors\nhttp://www.openstreetmap.org/copyright",
        "url": "https://{subdomain}.tile.thunderforest.com/$MAPSTYLE$/{z}/{x}/{y}.{ext}?apikey={api_key}".replace(
            "$MAPSTYLE$", style),
        "subdomains": ["a", "b", "c"],
        "api-key-ref": "thunderforest",
        "limit": 2,
    }


prefix_to_attrs = {
    "osm": osm_attrs,
    "tf": thunderforest_attrs,
    "geo": geoapify_attrs
}


def attrs_for_style(name):
    if name == "osm":
        return osm_attrs()

    prefix, style = name.split("-", 1)

    if prefix in prefix_to_attrs:
        return prefix_to_attrs[prefix](style)
    else:
        raise KeyError(f"Unknown map provider: {name}")


def provider_for_style(name, api_key_finder):
    attrs = attrs_for_style(name)
    if "api-key-ref" in attrs:
        api_key = api_key_finder.find_api_key(attrs["api-key-ref"])
    else:
        api_key = None
    return MapProvider(attrs, api_key)


def dbm_downloader(dbm_file):
    def get_key(key):
        return dbm_file.get(key, None)

    def set_key(key, value):
        if value:
            dbm_file.setdefault(key, value)

    return partial(caching_downloader, get_key, set_key, fetch_tiles)


def dbm_caching_renderer(provider, dbm_file):
    def render(map, tiles=None, **kwargs):
        map.provider = provider
        return geotiler.render_map(map, tiles, downloader=dbm_downloader(dbm_file), **kwargs)

    return render


class NullKeyFinder:
    def find_api_key(self, name):
        raise ValueError(f"I don't know any API keys. So can't give key for API '{name}'")


class EnvKeyFinder:
    def find_api_key(self, name, env=os.environ):
        e = f"API_KEY_{name}".upper()
        if e in env:
            return env[e]
        raise ValueError(f"No key for {name} ({e}) in environment")


class ArgsKeyFinder:
    def __init__(self, args):
        self.args = args

    def find_api_key(self, name):
        fullname = f"{name}-api-key"
        if fullname in self.args:
            return self.args[fullname]
        fallback = "api-key"
        if fallback in self.args:
            return self.args[fallback]
        raise ValueError(f"No api key for {name}")


class ConfigKeyFinder:
    def __init__(self):
        self.ourdir = Path.home().joinpath(".gopro-graphics")

    def find_api_key(self, name):
        config_file = self.ourdir / "map-api-keys.json"
        if config_file.exists():
            config = json.loads(config_file.read_text())

            if name in config:
                return config[name]

        raise ValueError(f"No api key for {name} in {config_file}")


class CompositeKeyFinder:
    def __init__(self, *others):
        self.others = others

    def find_api_key(self, name):
        for f in self.others:
            try:
                return f.find_api_key(name)
            except ValueError:
                pass
        raise ValueError(f"Couldn't find an api key for {name}")


class SingleKeyFinder:
    def __init__(self, key):
        self.key = key

    def find_api_key(self, name):
        return self.key


class CachingRenderer:

    def __init__(self, style="osm", api_key_finder=None):
        if api_key_finder is None:
            api_key_finder = NullKeyFinder()

        self.ourdir = Path.home().joinpath(".gopro-graphics")
        self.provider = provider_for_style(style, api_key_finder)

    @contextlib.contextmanager
    def open(self):
        self.ourdir.mkdir(exist_ok=True)

        with dbm.ndbm.open(str(self.ourdir.joinpath("tilecache.ndbm")), "c") as db:
            yield dbm_caching_renderer(self.provider, db)
