"""
Need to change database in main.py, otherwise local one overwritten
"""

from importlib.metadata import files
from test.utils.setup_database import init_tables
from test.utils.generate_image import *
from test.utils.clean_files_folder import *
from app.main import app
from fastapi.testclient import TestClient
import os

COUNT = 50
OFFSET = 0
FOLDER_PATH = "./test/files"
RECEIVED_FOLDER_PATH = FOLDER_PATH+"/received/"
THUMBNAIL_FOLDER_PATH = FOLDER_PATH+"/square/"
TEST_TAG_NAME = "cool tag"

client = TestClient(app)


def test_setup():
    init_tables()
    clean_files_folder()


def test_get_empty_list():
    response = client.get('/imagelist/%s/%s' % (COUNT, OFFSET))
    assert response.status_code == 200
    assert response.json() == {"sort_mode": 1, "data": {}}


def test_get_empty_tag_list():
    response = client.get('/taglist/%s/%s' % (COUNT, OFFSET))
    assert response.status_code == 200
    assert response.json() == {"sort_mode": 1, "data": {}}


def test_upload_image():
    files = [("files", ('img.png',
                        open('./test/utils/test_img.png', 'rb'), "image/png"))]
    response = client.post(
        '/image/', files=files)

    assert response.status_code == 200
    assert os.path.isfile(RECEIVED_FOLDER_PATH+response.json()["images"][0])


def test_upload_and_get_image():
    files = [("files", ('img.png',
                        open('./test/utils/test_img.png', 'rb'), "image/png"))]
    response = client.post(
        '/image/', files=files)

    assert response.status_code == 200

    file_name: str = response.json()["images"][0]
    response_get = client.get("/f/"+file_name)

    assert response_get.status_code == 200
    assert response_get.content != None


def test_upload_and_get_thumbnail():
    files = [("files", ('img.png',
                        open('./test/utils/test_img.png', 'rb'), "image/png"))]
    response = client.post(
        '/image/', files=files)

    assert response.status_code == 200

    file_name: str = response.json()["images"][0]
    response_get = client.get("/t/"+file_name)

    assert response_get.status_code == 200
    assert response_get.content != None


def test_upload_and_delete_image():
    files = [("files", ('img.png',
                        open('./test/utils/test_img.png', 'rb'), "image/png"))]
    response = client.post(
        '/image/', files=files)

    assert response.status_code == 200

    file_name: str = response.json()["images"][0]
    file_uuid: str = file_name.split(".")[0]
    delete_response = client.delete("/image/"+file_uuid)
    assert delete_response.status_code == 200


def test_upload_and_tag_image() -> str:
    files = [("files", ('img.png',
                        open('./test/utils/test_img.png', 'rb'), "image/png"))]
    response = client.post(
        '/image/', files=files)
    assert response.status_code == 200

    file_name: str = response.json()["images"][0]
    file_uuid: str = file_name.split(".")[0]

    body = {
        "tag": TEST_TAG_NAME,
        "images": [file_uuid]
    }

    tag_response = client.post('/tag/', data=body)
    assert tag_response.status_code == 200
    return file_uuid


def test_add_and_get_tag():
    test_setup()
    file_uuid = test_upload_and_tag_image()
    response = client.get('/taglist/%s/%s' % (COUNT, OFFSET))
    assert response.status_code == 200
    assert response.json()["data"]["0"]["tname"] == "cool tag"
    # uuid here is thumbnail
    assert response.json()["data"]["0"]["uuid"] == file_uuid

    image_list_response = client.get(
        '/imagelist/%s/%s?tag=%s' % (COUNT, OFFSET, TEST_TAG_NAME, ))

    assert image_list_response.status_code == 200
    assert image_list_response.json()["data"]["0"]["uuid"] == file_uuid


def test_add_and_remove_from_tag():
    test_setup()
    file_uuid = test_upload_and_tag_image()
    body = {
        "tag": TEST_TAG_NAME,
        "images": [file_uuid]
    }
    response = client.post('/untag/', data=body)
    assert response.status_code == 200


def test_fail_delete_image():
    response = client.delete("/image/"+"impossible_name")
    assert response.status_code == 404


def test_fail_get_image():
    response = client.get("/f/"+"impossible_name")  # uuid4 are longer
    assert response.status_code == 404


def test_fail_get_thumbnail():
    response = client.get("/t/"+"impossible_name")  # uuid4 are longer
    assert response.status_code == 404
