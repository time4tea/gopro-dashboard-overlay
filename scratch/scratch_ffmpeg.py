import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from gopro_overlay.config import Config
from gopro_overlay.dimensions import Dimension
from gopro_overlay.ffmpeg import FFMPEG
from gopro_overlay.ffmpeg_overlay import FFMPEGOverlay, FFMPEGOverlayVideo, FFMPEGOptions, FFMPEGNull
from gopro_overlay.ffmpeg_profile import FFMPEGProfiles
from gopro_overlay.progresstrack import ProgressBarProgress

if __name__ == "__main__":

    overlay = False

    ffmpeg_exe = FFMPEG()


    dimension = Dimension(2704, 1520)
    # if overlay:
    #     generator = FFMPEGOverlayVideo(input="/data/richja/gopro/GH010064.MP4", output="output.mp4", overlay_size=dimension)
    # else:
    #
    #     options =  FFMPEGOptions(output=["-vcodec", "h264_nvenc", "-rc:v", "cbr", "-b:v", "25M", "-bf:v", "3", "-profile:v", "high", "-spatial-aq", "true", "-movflags", "faststart"])
    #
    #     generator = FFMPEGOverlay(ffmpeg = ffmpeg_exe, output=Path("output.mp4"), overlay_size=dimension, options=options)

    generator = FFMPEGNull()

    progress = ProgressBarProgress("Render", delta=True)

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

        progress.start(300000)

        for i in range(0, 300000):
            writer.write(image.tobytes())
            progress.update(1)

    print("done writing frames")
