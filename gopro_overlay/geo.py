import contextlib
import dbm.ndbm
import itertools
import os
import pathlib
from functools import partial
from typing import Optional, Tuple

import geotiler
from geotiler.cache import caching_downloader
from geotiler.provider import MapProvider
from geotiler.tile.io import fetch_tiles

from gopro_overlay.config import Config
from gopro_overlay.geo_render import my_render_map

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
    ["local"],
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


def local_attrs(style):
    return {
        "name": "Local",
        "url": "http://localhost:8000/{z}/{x}/{y}.{ext}",
        "cache": False,
        "limit": 2
    }


prefix_to_attrs = {
    "osm": osm_attrs,
    "tf": thunderforest_attrs,
    "geo": geoapify_attrs,
    "local": local_attrs,
}


def configured_style(loader: Config, name: str) -> Optional[dict]:
    config_file = loader.maybe("map-styles.json")
    if config_file.exists():

        if name in config_file.content:
            attrs = config_file.content[name]

            if not "url" in attrs:
                raise ValueError(f"Required key 'url' not found for {name} in {config_file.location}")

            return attrs
    return None


def attrs_for_style(name):
    if name == "osm":
        return osm_attrs()

    if "-" in name:
        prefix, style = name.split("-", 1)
    else:
        prefix = style = name

    if prefix in prefix_to_attrs:
        return prefix_to_attrs[prefix](style)
    else:
        raise KeyError(f"Unknown map provider: {name}")


def dbm_downloader(dbm_file):
    def get_key(key):
        return dbm_file.get(key, None)

    def set_key(key, value):
        if value:
            dbm_file.setdefault(key, value)

    return partial(caching_downloader, get_key, set_key, fetch_tiles)


def dbm_caching_renderer(provider: MapProvider, dbm_file):
    def render(map, tiles=None, **kwargs):
        map.provider = provider
        return my_render_map(map, tiles, downloader=dbm_downloader(dbm_file), **kwargs)

    return render


def no_caching_renderer(provider: MapProvider):
    def render(map, tiles=None, **kwargs):
        map.provider = provider

        return geotiler.map.render_map(map, tiles, **kwargs)

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
        key = self.args.map_api_key
        if key is not None:
            return key

        raise ValueError(f"No api key for {name}")


class ConfigKeyFinder:
    def __init__(self, loader: Config):
        self.loader = loader

    def find_api_key(self, name):
        config = self.loader.maybe("map-api-keys.json")

        if config.exists():
            if name in config.content:
                return config.content[name]

        raise ValueError(f"No api key for {name} in {config.location}")


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


def api_key_finder(loader: Config, args):
    return CompositeKeyFinder(
        ArgsKeyFinder(args),
        EnvKeyFinder(),
        ConfigKeyFinder(loader)
    )


class MapStyler:
    def __init__(self, api_key_finder=NullKeyFinder()):
        self.api_key_finder = api_key_finder

    def provide(self, style: str = "osm") -> Tuple[dict, str]:
        return self.provider_for_style(style, self.api_key_finder)

    def provider_for_style(self, name, api_key_finder) -> Tuple[dict, str]:
        attrs = attrs_for_style(name)
        if "api-key-ref" in attrs:
            api_key = api_key_finder.find_api_key(attrs["api-key-ref"])
        else:
            api_key = None
        return attrs, api_key


class MapRenderer:

    def __init__(self, cache_dir: pathlib.Path, styler: MapStyler):
        self.cache_dir = cache_dir
        self.styler = styler

    @contextlib.contextmanager
    def open(self, style: str = "osm"):

        attrs, key = self.styler.provide(style)

        map = MapProvider(attrs, key)

        if attrs.get("cache", True):
            with dbm.ndbm.open(str(self.cache_dir.joinpath("tilecache.ndbm")), "c") as db:
                yield dbm_caching_renderer(map, db)
        else:
            yield no_caching_renderer(map)
