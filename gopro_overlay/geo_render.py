import asyncio
import io
import itertools
from typing import List

import PIL
from PIL.Image import Image
from geotiler.map import _find_top_left_tile, _tile_coords, _tile_offsets, Tile
from geotiler.tile.img import _error_image

from gopro_overlay.log import log


# Attempt at re-implementing the rendering part of geotiler with a view on performance
# Use downloader as per geotiler

class ImageTileCache:

    def __init__(self):
        self.cache = {}

    async def do_async_download(self, downloader, tiles: List[Tile]):
        gen = downloader(tiles, 1)
        l = []
        async for g in gen:
            l.append(g)
        return l

    def do_download(self, downloader, tiles: List[Tile]) -> List[Tile]:
        task = self.do_async_download(downloader, tiles)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(task)

    def as_image(self, data):
        f = io.BytesIO(data)
        return PIL.Image.open(f).convert('RGBA')

    def populate(self, downloader, tiles: List[Tile], error_image):

        # Populate image directly for those we know already
        def c(t):
            if t.url in self.cache:
                return t._replace(img=self.cache[t.url])
            return t

        tiles = [c(t) for t in tiles]

        have = [t for t in tiles if t.img is not None]
        have_not = [t for t in tiles if t.img is None]

        # Now use existing download to download
        downloaded = self.do_download(downloader, have_not)

        converted = []

        for d in downloaded:
            if d.img is None:
                img = error_image
            else:
                try:
                    img = self.as_image(d.img)
                except OSError as e:
                    # somehow the image data is invalid...
                    log(f"Unable to load image data from {d.url} - {e}")
                    img = error_image

            self.cache[d.url] = img
            converted.append(d._replace(img=img))

        return list(itertools.chain(have, converted))


cache = ImageTileCache()


def my_render_map(map, tiles, downloader, **kwargs):
    tile_url = map.provider.tile_url

    coord, offset = _find_top_left_tile(map)
    coords = _tile_coords(map, coord, offset)
    offsets = _tile_offsets(map, offset)
    urls = (tile_url(c, map.zoom) for c in coords)
    tiles = list((Tile(u, o, None, None) for u, o in zip(urls, offsets)))

    provider = map.provider

    tiles = cache.populate(downloader, tiles, _error_image(provider.tile_width, provider.tile_height))

    image = PIL.Image.new('RGBA', tuple(map.size))

    for tile in tiles:
        image.paste(tile.img, tile.offset)

    return image
