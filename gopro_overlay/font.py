from PIL import ImageFont


def load_font(font: str, size: int = 32):
    return ImageFont.truetype(font=font, size=size)
