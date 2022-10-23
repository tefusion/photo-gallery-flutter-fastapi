from .utils.generate_image import *

from app.file_storage_handler import FileStorageHandler
import os
from .utils.clean_files_folder import *
import pytest

db_name = "test_images"
FOLDER_PATH = "./test/files"
RECEIVED_FOLDER_PATH = FOLDER_PATH+"/received/"
THUMBNAIL_FOLDER_PATH = FOLDER_PATH+"/square/"
THUMBNAIL_SIZE = 200
file_handler = FileStorageHandler(folder_path=FOLDER_PATH)


def test_add_single_image():
    image_path = "test1.png"
    fake_file = get_fake_image_file_as_bytes()
    file_handler.save_file(fake_file, image_path)
    assert RECEIVED_FOLDER_PATH + \
        image_path == file_handler.get_image_path(image_path)


def test_add_image_and_generate_thumbnail():
    image_path = "test2.png"
    fake_file = get_fake_image_file()
    fake_file.save(RECEIVED_FOLDER_PATH+image_path)

    file_handler.create_thumbnail(image_path, THUMBNAIL_SIZE)
    assert THUMBNAIL_FOLDER_PATH + \
        image_path == file_handler.get_thumbnail_path(image_path)


def test_delete_image():
    image_path = "test3.png"
    fake_file = get_fake_image_file()
    fake_file.save(RECEIVED_FOLDER_PATH+image_path)
    assert os.path.isfile(RECEIVED_FOLDER_PATH+image_path)
    file_handler.create_thumbnail(image_path, THUMBNAIL_SIZE)
    file_handler.remove_image(image_path)
    assert not os.path.isfile(RECEIVED_FOLDER_PATH+image_path)


if __name__ == '__main__':
    clean_files_folder()
