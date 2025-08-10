import contextlib
import itertools
import os
import pathlib
from functools import partial
from typing import Optional, Tuple, List, Dict

import geotiler
from geotiler.cache import caching_downloader
from geotiler.provider import MapProvider
from geotiler.tile.io import fetch_tiles
from sqlitedict import SqliteDict

from gopro_overlay.config import Config
from gopro_overlay.geo_render import my_render_map


class PrefixMapStyleConfig:

    def __init__(self, prefix):
        self.prefix = prefix

    def styles(self) -> List[str]:
        if self.prefix:
            return [f"{self.prefix}-{s}" for s in self._styles()]
        else:
            return self._styles()

    def attributes(self, style: str) -> Dict:
        if self.prefix:
            return self._attributes(style[len(self.prefix) + 1:])
        else:
            return self._attributes(style)

    def _attributes(self, style) -> Dict:
        raise NotImplementedError()

    def _styles(self) -> List[str]:
        raise NotImplementedError()


class OSMStyleConfig(PrefixMapStyleConfig):

    def __init__(self):
        super().__init__("")

    def _styles(self) -> List[str]:
        return ["osm"]

    def _attributes(self, style: str) -> Dict:
        assert style in self._styles()
        return {
            "name": "OpenStreetMap",
            "attribution": "© OpenStreetMap contributors\nhttp://www.openstreetmap.org/copyright",
            "url": "http://{subdomain}.tile.openstreetmap.org/{z}/{x}/{y}.{ext}",
            "subdomains": ["a", "b", "c"],
            "limit": 2
        }


class CyclOSMStyleConfig(PrefixMapStyleConfig):

    def __init__(self):
        super().__init__("")

    def _styles(self) -> List[str]:
        return ["cyclosm"]

    def _attributes(self, style: str) -> Dict:
        assert style in self._styles()
        return {
            "name": "CyclOSM",
            "attribution": "Maps © CyclOSM\nhttps://www.cyclosm.org/ Data © OpenStreetMap contributors\nhttp://www.openstreetmap.org/copyright",
            "url": "https://{subdomain}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
            "subdomains": ["a", "b", "c"],
            "limit": 2
        }


class GeoapifyStyleConfig(PrefixMapStyleConfig):

    def __init__(self):
        super().__init__("geo")

    def _styles(self) -> List[str]:
        return [
            "osm-carto", "osm-bright", "osm-bright-grey", "osm-bright-smooth",
            "klokantech-basic", "osm-liberty", "maptiler-3d", "toner", "toner-grey", "positron",
            "positron-blue", "positron-red", "dark-matter", "dark-matter-brown", "dark-matter-dark-grey",
            "dark-matter-dark-purple", "dark-matter-purple-roads", "dark-matter-yellow-roads"
        ]

    def _attributes(self, style: str) -> Dict:
        assert style in self._styles()
        return {
            "name": "Geoapify Map",
            "attribution": "Maps © Geoapify\nhttps://www.geoapify.com/\nData © OpenStreetMap "
                           "contributors\nhttp://www.openstreetmap.org/copyright",
            "url": "https://maps.geoapify.com/v1/tile/$MAPSTYLE$/{z}/{x}/{y}.png?apiKey={api_key}".replace(
                "$MAPSTYLE$", style),
            "api-key-ref": "geoapify",
            "limit": 2,
        }


class ThunderforestStyleConfig(PrefixMapStyleConfig):

    def __init__(self):
        super().__init__("tf")

    def _styles(self) -> List[str]:
        return [
            "cycle", "transport", "landscape",
            "outdoors", "transport-dark", "spinal-map",
            "pioneer", "mobile-atlas", "neighbourhood",
            "atlas"
        ]

    def _attributes(self, style: str) -> Dict:
        assert style in self._styles()
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


class TianDiTuStyleConfig(PrefixMapStyleConfig):

    def __init__(self):
        super().__init__("tdt")

    def _styles(self) -> List[str]:
        return [
            "vec", "cva", "img", "cia",
            "ter", "cta", "ibo"
        ]

    def _attributes(self, style: str) -> Dict:
        assert style in self._styles()
        return {
            "name": "TianDiTu",
            "attribution": "转自天地图\nhttp://www.tianditu.gov.cn/",
            "url": "http://t{subdomain}.tianditu.gov.cn/$MAPSTYLE$_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=$MAPSTYLE$&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk={api_key}".replace(
                "$MAPSTYLE$", style),
            "subdomains": ["0", "1", "2", "3", "4", "5", "6", "7"],
            "api-key-ref": "tianditu",
            "limit": 2,
        }


class LocalStyleConfig(PrefixMapStyleConfig):

    def __init__(self):
        super().__init__("")

    def _styles(self) -> List[str]:
        return ["local"]

    def _attributes(self, style: str) -> Dict:
        assert style in self._styles()
        return {
            "attribution": "Custom",
            "name": "Local",
            "url": "http://localhost:8000/{z}/{x}/{y}.{ext}",
            "cache": False,
            "limit": 2
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


configurations = [OSMStyleConfig(), CyclOSMStyleConfig(), ThunderforestStyleConfig(), GeoapifyStyleConfig(), TianDiTuStyleConfig(),
                  LocalStyleConfig()]


def available_map_styles() -> List[str]:
    return sorted(list(itertools.chain.from_iterable(
        [p.styles() for p in configurations]
    )))


def attrs_for_style(name):
    for config in configurations:
        if name in config.styles():
            return config.attributes(name)

    raise KeyError(f"Unknown map style: {name}")


def sqlite_downloader(db: SqliteDict):
    def get_key(key):
        return db.get(key, None)

    def set_key(key, value):
        if value:
            db.setdefault(key, value)

    return partial(caching_downloader, get_key, set_key, fetch_tiles)


def sqlite_caching_renderer(provider: MapProvider, db: SqliteDict):
    def render(map, tiles=None, **kwargs):
        map.provider = provider
        return my_render_map(map, tiles, downloader=sqlite_downloader(db), **kwargs)

    return render


def memory_caching_renderer(provider: MapProvider):
    def render(map, tiles=None, **kwargs):
        map.provider = provider

        return my_render_map(map, tiles, downloader=fetch_tiles)

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
            with SqliteDict(
                    filename=str(self.cache_dir.joinpath("tilecache.sqlite")),
                    autocommit=True
            ) as db:
                yield sqlite_caching_renderer(map, db)
        else:
            yield memory_caching_renderer(map)
