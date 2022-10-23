from PIL import Image
from io import BytesIO


def get_fake_image_file_as_bytes() -> BytesIO:
    image = get_fake_image_file()
    byteIO = BytesIO()
    image.save(byteIO, format='PNG')
    return byteIO


def get_fake_image_file() -> Image:
    return Image.new("RGB", (128, 128), "#FF00FF")
