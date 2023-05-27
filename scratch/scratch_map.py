import argparse
import pathlib

from gopro_overlay.config import Config
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGOverlay
from gopro_overlay.geo import api_key_finder, CachingRenderer, MapStyleProvider
from gopro_overlay.point import Coordinate, Point
from gopro_overlay.timeunits import timeunits
from gopro_overlay.widgets.map import MovingMap
from gopro_overlay.widgets.widgets import Scene, SimpleFrameSupplier

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Overlay gadgets on to GoPro MP4",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    args = parser.parse_args()
    config_dir = pathlib.Path.home() / ".gopro-graphics"

    key_finder = api_key_finder(Config(config_dir), args)

    dimension = Dimension(512, 512)
    ffmpeg = FFMPEGOverlay(output=pathlib.Path("render/test.MP4"), overlay_size=dimension)

    length = timeunits(seconds=30)

    current = timeunits(seconds=0)

    map_style_provider = MapStyleProvider(api_key_finder=key_finder)

    frame_supplier = SimpleFrameSupplier(dimension)

    with ffmpeg.generate() as writer:
        with CachingRenderer(
                cache_dir=config_dir,
                provider=map_style_provider.provide()).open() as renderer:

            scene = Scene(
                widgets=[
                    MovingMap(
                        at=Coordinate(0, 0),
                        location=lambda: Point(51.50337467, -0.11225266),
                        azimuth=lambda: 0,
                        renderer=renderer,
                        rotate=False,
                        zoom=16,
                        size=512,
                        always_redraw=True
                    )
                ]
            )

            while current < length:
                image = scene.draw(frame_supplier.drawing_frame())
                writer.write(image.tobytes())
                current = current + timeunits(seconds=0.1)
