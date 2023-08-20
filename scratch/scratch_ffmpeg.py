import datetime

from PIL import Image, ImageDraw, ImageFont

from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg_overlay import FFMPEGOverlay, FFMPEGOverlayVideo

if __name__ == "__main__":

    overlay = True

    dimension = Dimension(1920, 1080)
    if overlay:
        generator = FFMPEGOverlayVideo(input="/data/richja/gopro/GH010064.MP4", output="output.mp4", overlay_size=dimension)
    else:
        generator = FFMPEGOverlay(output="output.mp4", overlay_size=dimension)

    with generator.generate() as writer:

        for i in range(1, 100):
            image = Image.new("RGBA", (dimension.x, dimension.y), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            font = ImageFont.truetype(font="Roboto-Medium.ttf", size=36)

            draw.text(
                (500, 500),
                datetime.datetime.now().strftime("%H:%M:%S.%f"),
                font=font,
                fill=(255, 255, 255),
                stroke_width=2,
                stroke_fill=(0, 0, 0)
            )

            writer.write(image.tobytes())

    print("done writing frames")
