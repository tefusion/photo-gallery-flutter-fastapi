from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Form


from app.data_server import *
from app.system_info import SystemInfo


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # for debugging just wildcard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# change to test_images for running tests
#imageServer = ImageServer("images", "./files")
imageServer = ImageServer("test_images", "./test/files")

systemInfo = SystemInfo()

# doesn't need to be async because this method doesn't access the database, all other methods do
# fast api auto threads non async def functions


@app.get("/f/{path}")
def get_File(path):
    return imageServer.return_image(path)


@app.get("/t/{path}")
def get_thumbnail(path: str):
    return imageServer.return_thumbnail(path)


@app.get("/imagelist/{count}/{offset}", response_model=ImageListResponse)
async def get_image_list(count: int, offset: int, sort_mode: str = None, tag: str = None):
    sort_mode_type = convert_sort_mode(sort_mode)
    return imageServer.get_image_list(offset, count, sort_mode_type, tag)


@app.get("/taglist/{count}/{offset}", response_model=TagListResponse)
async def get_tag_list(count: int, offset: int, sort_mode: str = None, tag: str = ""):
    sort_mode_type = convert_sort_mode(sort_mode)
    return imageServer.get_tag_list(offset, count, sort_mode_type, tag)


@app.get("/autocomplete")
async def autocomplete(tag_start: str = ""):
    return imageServer.get_tags_starting_with_pattern(tag_start)


@app.post("/images/", response_model=UploadedImagesResponse)  # multiple
async def upload_images(title: str = Form(...), description: str = Form(...),
                        files: List[UploadFile] = File(...), tag: str = Form(...), compressed: Optional[bool] = None):
    multi_file_data = MultiFileData(
        title=title, description=description, files=files, tag=tag, compressed=compressed)
    return await imageServer.upload_multiple_images(multi_file_data)


@app.delete("/image/{image_id}")
async def delete_image(image_id: str):
    imageServer.delete_image(image_id)
    return Response(None, 200)


@app.post("/tag/")
async def tag_images(tag: str = Form(...), images: List[int] = Form(...)):
    tagData = TagData(tag=tag, images=images)
    imageServer.tag_images(tagData)
    return Response(None, 200)


@app.post("/untag/")
async def untag_images(tag: str = Form(...), images: List[int] = Form(...)):
    tagData = TagData(tag=tag, images=images)
    return imageServer.remove_image_from_tag(tagData)


@app.put("/reorder/{tagname}/{idShip}")
async def reorder_images(tagname: str, idShip: int, idDestination: int, mode: int = 1):
    imageServer.reorder_images(idShip, idDestination, mode, tagname)
    return Response(None, 200)


@app.put("/tagname/{oldTagName}")
async def change_tag_name(oldTagName: str = "", newTagName: str = ""):
    return imageServer.change_tag_name(oldTagName, newTagName)


@app.get("/randomize")
def set_new_random_seed():
    imageServer.set_new_rand_seed()
    return Response(None, 200)


@app.get("/disk_usage")
def get_disk_usage():
    return systemInfo.get_disk_usage()


@app.post("/image/", response_model=UploadedImagesResponse)
async def upload_image(files: List[UploadFile] = File(...)):
    # method to allow single file upload for testing
    multi_file_data = MultiFileData(
        title="title", description="description", files=files, tag="", compressed=False)
    return await imageServer.upload_multiple_images(multi_file_data)
