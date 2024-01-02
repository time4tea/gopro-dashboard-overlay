import argparse
import pathlib

from gopro_overlay.config import Config
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_overlay import FFMPEGOverlay
from gopro_overlay.ffmpeg_profile import FFMPEGProfiles
from gopro_overlay.geo import api_key_finder, MapRenderer, MapStyler
from gopro_overlay.point import Coordinate, Point
from gopro_overlay.timeunits import timeunits
from gopro_overlay.units import units
from gopro_overlay.widgets.map import MovingMap
from gopro_overlay.widgets.widgets import Scene, SimpleFrameSupplier

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Overlay gadgets on to GoPro MP4",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    args = parser.parse_args()
    config_dir = pathlib.Path.home() / ".gopro-graphics"

    config = Config(config_dir)
    key_finder = api_key_finder(config, args)

    dimension = Dimension(512, 512)

    profile = FFMPEGProfiles(config).load_profile("mov")

    ffmpeg = FFMPEGOverlay(
        ffmpeg=FFMPEG(print_cmds=True),
        options=profile,
        output=pathlib.Path("render/test.mov"), overlay_size=dimension
    )

    length = timeunits(seconds=30)

    current = timeunits(seconds=0)

    frame_supplier = SimpleFrameSupplier(dimension)

    count = 0

    with ffmpeg.generate() as writer:
        with MapRenderer(
                cache_dir=config_dir,
                styler=MapStyler(api_key_finder=key_finder)).open("osm") as renderer:

            scene = Scene(
                widgets=[
                    MovingMap(
                        at=Coordinate(0, 0),
                        location=lambda: Point(51.50337467, -0.11225266),
                        azimuth=lambda: units.Quantity(count, "degree"),
                        renderer=renderer,
                        rotate=True,
                        zoom=19,
                        size=512,
                        always_redraw=True
                    )
                ]
            )

            while current < length:
                image = scene.draw(frame_supplier.drawing_frame())
                writer.write(image.tobytes())
                current = current + timeunits(seconds=0.1)
                count += units.Quantity(5, "degree")