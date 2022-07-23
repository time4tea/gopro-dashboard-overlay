import datetime

from PIL import Image, ImageDraw, ImageFont

from gopro_overlay.dimensions import Dimension
from gopro_overlay.execution import InProcessExecution
from gopro_overlay.ffmpeg import FFMPEGGenerate, FFMPEGOverlayMulti, FFMPEGRunner, FFMPEGExecute

if __name__ == "__main__":

    overlay = True

    dimension = Dimension(1920, 1080)
    if overlay:
        generator = FFMPEGOverlayMulti(
            inputs=[
                "/home/richja/dev/gopro-graphics/render/2022-03-17-richmond-park-1.mp4",
                "/home/richja/dev/gopro-graphics/render/2022-03-17-richmond-park-1.mp4",
            ],
            output="output.mp4",
            overlay_size=dimension,
            runner=FFMPEGExecute(InProcessExecution())
        )
    else:
        generator = FFMPEGGenerate(output="output.mp4", overlay_size=dimension)

    with generator.generate() as writer:

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

        for i in range(1, 120 * 10 * 2):
            print(i)
            writer.write(image.tobytes())

    print("done writing frames")
