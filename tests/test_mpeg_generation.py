from gopro_overlay.common import temporary_file
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEGOverlay
from gopro_overlay.font import load_font
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets.widgets import Scene, CachingText

font = load_font("Roboto-Medium.ttf")


def test_overlay_only():
    with temporary_file(suffix=".MP4") as output:
        print(f"Movie is at {output}")

        dimension = Dimension(1920, 1080)
        ffmpeg = FFMPEGOverlay(
            output=output,
            overlay_size=dimension
        )

        count = [0]

        def nextval():
            count[0] += 1
            return str(count[0])

        scene = Scene(dimensions=dimension, widgets=[
            CachingText(at=Coordinate(800, 400), value=nextval, font=font.font_variant(size=160))
        ])

        with ffmpeg.generate() as mp4:
            for i in range(1, 50):
                image = scene.draw()
                mp4.write(image.tobytes())

        pass  # breakpoint here to view the file...
