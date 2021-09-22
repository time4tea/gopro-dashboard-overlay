import datetime

from PIL import Image, ImageDraw, ImageFont
from numpy import asarray

from gopro_overlay.ffmpeg import FFMPEGOverlay, FFMPEGGenerate

if __name__ == "__main__":

    overlay = True

    if overlay:
        generator = FFMPEGOverlay(input="/data/richja/gopro/GH010064.MP4.copy", output="output.mp4")
    else:
        generator = FFMPEGGenerate(output="output.mp4")

    with generator.generate() as writer:

        for i in range(1, 100):
            image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
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

            writer.write(asarray(image).tobytes())

    print("done writing frames")
