"""
Contains functions to cut thumbnails and save an image at a specified path
"""

from PIL import Image
import io
import aiofiles
import os


class FileHandler:
    def __init__(self, folder_path) -> None:
        self.directory_path = folder_path+"/received/"
        self.thumbnail_path = folder_path+"/square/"

    async def save_file(self, file, new_filename):
        async with aiofiles.open(self.directory_path+new_filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

    async def save_file_compressed(self, file, new_filename):
        tempFile = file.file
        im = Image.open(io.BytesIO(tempFile.read()))
        im.convert("RGB").save(self.directory_path+new_filename,
                               format="JPEG", quality=70, optimize=True)

    def create_thumbnail(self, image_path: str, size: int):
        """
        :param image_path: str
        :param size: int

        Uses PILLOW/PIL.Image to cut the middle out of the image and resize it to the size to have a thumbnail in square format
        """
        im = Image.open(self.directory_path+image_path)
        width, height = im.size
        # cut into square
        if width > height:
            left = width/2-height/2
            right = width/2+height/2
            thumbnail = im.crop((left, 0, right, height))
        else:
            top = int(height/2+width/2)
            bottom = int(height/2-width/2)
            thumbnail = im.crop((0, bottom, width, top))

        thumbnail.thumbnail([size, size])

        thumbnail.save(self.thumbnail_path+image_path)
        # this is the option of not saving the image, but sending it directly
        # img_byte_arr = io.BytesIO()
        # thumbnail.save(img_byte_arr, format='PNG')
        # return StreamingResponse(iter([img_byte_arr.getvalue()]), media_type='image/png')

    def get_thumbnail_path(self, image_path: str) -> str:
        # if thumbnail exists return it
        if os.path.isfile(self.thumbnail_path+image_path):
            return self.thumbnail_path+image_path

    def get_image_path(self, image_path):
        return self.directory_path+image_path

    def remove_image(self, file_path):
        os.remove(self.directory_path+file_path)
        os.remove(self.thumbnail_path+file_path)
