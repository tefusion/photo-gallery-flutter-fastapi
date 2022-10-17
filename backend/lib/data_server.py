from fastapi.responses import FileResponse, StreamingResponse
from fastapi import File, UploadFile

import os
# import PIL
from PIL import Image
import io

import uuid
import aiofiles


import mysql.connector
import datetime

from dotenv import load_dotenv

from random import randint

from lib.models import *
from lib.data_server_get import *


class ImageServer:
    """
    Handles everything related to database 
    """

    def __init__(self):
        """
        Creates connection to sqlServer
        """
        self.directoryPath = "./Files/Received/"
        self.thumbnailPath = "./Files/square/"
        self.randId: int = randint(0, 1000000)
        load_dotenv()
        PASSWORD = os.getenv("DB_PASSWORD")
        self.db = mysql.connector.connect(
            host="localhost",
            database="images",
            user="root",
            password=PASSWORD
        )

    def return_image(self, ImagePath):
        """
        param ImagePath: str
        returns specified file at Path
        """
        return FileResponse(self.directoryPath+ImagePath)

    def return_thumbnail(self, ImagePath: str, size: int):
        """
        same as returnImage, just returns smaller square cut from it
        """
        if os.path.isfile(self.thumbnailPath+ImagePath):  # if thumbnail exists return it
            thumbnail = FileResponse(self.thumbnailPath+ImagePath)
        else:  # if thumbnail doesn't exist create it, this was necessary at the start since thumbnails weren't saved previously
            # can be removed in a future version
            self.create_thumbnail(ImagePath, size)
            thumbnail = FileResponse(self.thumbnailPath+ImagePath)

        return thumbnail

    def create_thumbnail(self, ImagePath: str, size: int):
        """
        param ImagePath: str
        param size: int

        Uses PILLOW/PIL.Image to cut the middle out of the image and resize it to the size to have a thumbnail in square format
        """
        im = Image.open(self.directoryPath+ImagePath)
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

        thumbnail.save(self.thumbnailPath+ImagePath)
        # this is the option of not saving the image, but sending it directly
        #img_byte_arr = io.BytesIO()
        #thumbnail.save(img_byte_arr, format='PNG')
        # return StreamingResponse(iter([img_byte_arr.getvalue()]), media_type='image/png')

    def get_image_list(self, offset: int, count: int, sortMode: int, tag: str):
        """
        param offset: str (but has to actually be an int, since all gets passed in sql as a str int values already passed as str)
        param count: str: Limit count
        param sortMode: int see SortMode enum
        param tag: str: for future use of retrieving only tags starting with this pattern
        """
        try:
            mycursor = self.db.cursor(dictionary=True)
        except:
            self.__init__()
            mycursor = self.db.cursor(dictionary=True)
        return get_image_list_from_server(mycursor, offset=offset, count=count, sortMode=sortMode, tag=tag, randId=self.randId)

    def get_tag_list(self, offset: int, count: int, sortMode: int, tag: str = ""):
        """
        params: offset, count, sortMode
        gets tagList with thumbnails from sql server
        """
        try:
            mycursor = self.db.cursor(dictionary=True)
        except:
            self.__init__()
            mycursor = self.db.cursor(dictionary=True)
        return get_tag_list_from_server(mycursor, offset=offset, count=count, sortMode=sortMode, randId=self.randId, tag=tag)


    def add_to_image_table(self, file_name, fileData: FileData, tag=""):
        mycursor = self.db.cursor()

        if tag != "" and tag != " ":
            tagData = TagData(tag=tag, images=[])

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO image (title, description, file_path, time_created) VALUES (%s, %s, %s, %s)"
        val = (fileData.title, fileData.description, file_name, now)
        mycursor.execute(sql, val)
        if tag != "" and tag != " ":
            tagData.images.append(mycursor.lastrowid)
        self.db.commit()
        mycursor.close()
        if tag != "" and tag != " ":
            self.tagImages(tagData=tagData)

    # for multiple images:

    async def upload_multiple_images(self, multiFileData: MultiFileData):

        file_names = []
        for file in multiFileData.files:
            fileNameArr = file.filename.split(".")
        # new generated file name with same file extension
            if multiFileData.compressed == False:
                new_filename = str(uuid.uuid4())+"." + \
                    fileNameArr[len(fileNameArr)-1]
                await self.save_file(file, new_filename)
                self.create_thumbnail(new_filename, 200)
                file_names.append(new_filename)
            else:  # in compressed mode all images saved as jpeg
                new_filename = str(uuid.uuid4())+".jpg"
                await self.save_file_compressed(file, new_filename)
                self.create_thumbnail(new_filename, 200)
                file_names.append(new_filename)

        self.add_multiple_images_to_table(
            file_names, multiFileData.title, multiFileData.description, multiFileData.tag)

   
    def add_multiple_images_to_table(self, file_names, title, description, tag):
        try:
            mycursor = self.db.cursor()
        except Exception as e:
            self.__init__()
            mycursor = self.db.cursor(dictionary=True)

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if tag != "" and tag != " ":
            tagData = TagData(tag=tag, images=[])
        for file_name in file_names:
            sql = "INSERT INTO image (title, description, file_path, time_created) VALUES (%s, %s, %s, %s)"
            val = (title, description, file_name, now)
            mycursor.execute(sql, val)
            if tag != "" and tag != " ":
                tagData.images.append(mycursor.lastrowid)
        self.db.commit()
        mycursor.close()
        if tag != "" and tag != " ":
            self.tag_images(tagData=tagData)

    def delete_image(self, image_id: str):
        mycursor = self.db.cursor()
        mycursor.execute("SELECT file_path FROM image WHERE id="+image_id)
        try:
            for row in mycursor:
                file_path = row[0]
            mycursor.execute("DELETE FROM image WHERE id="+image_id)
            mycursor.execute("DELETE FROM tagmap WHERE image_id="+image_id)
            self.db.commit()
            os.remove(self.directoryPath+file_path)
            os.remove(self.thumbnailPath+file_path)

        except:
            pass

        finally:
            mycursor.close()

    async def save_file(self, file, new_filename):
        async with aiofiles.open(self.directoryPath+new_filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

    async def save_file_compressed(self, file, new_filename):
        tempFile = file.file
        im = Image.open(io.BytesIO(tempFile.read()))
        im.convert("RGB").save(self.directoryPath+new_filename,
                               format="JPEG", quality=70, optimize=True)

    def add_new_tag(self, tagname: str):
        """
        Adds new tag with tagname
        """
        mycursor = self.db.cursor()
        sql = "INSERT INTO tag (tname) VALUES (%s)"
        mycursor.execute(sql, (tagname,))
        self.db.commit()
        mycursor.close()

    def find_tag_id(self, tname: str):
        mycursor = self.db.cursor()
        sql = "SELECT tag_id FROM tag WHERE tname=%s LIMIT 1"
        mycursor.execute(sql, (tname,))
        tag_id = None  # make better way to do this .-.
        for row in mycursor:
            tag_id = row[0]
        mycursor.close()
        return tag_id

    def tag_images(self, tagData: TagData):
        """
        Input Value TagData
        Adds images in tagData.images to tagData.tag in tagmap
        """
        mycursor = self.db.cursor()
        # make better way to do this .-.
        # this is just a quick check if the tag even exists
        # if it doesn't just add the first image to it so it actually exists
        tag_id = self.find_tag_id(tagData.tag)
        if tag_id == None:
            self.add_new_tag(tagData.tag)
            tag_id = self.find_tag_id(tagData.tag)

        sql = "SELECT MAX(pos) as last_pos FROM tagmap where tag_id="+str(tag_id)
        mycursor.execute(sql)
        for row in mycursor:
            if row[0] == None:
                last_pos = 0
            else:
                last_pos = row[0]+1

        sql = "SELECT image_id FROM tagmap where tag_id="+str(tag_id)
        mycursor.execute(sql)
        taggedImageIds = []
        for row in mycursor:
            taggedImageIds.append(row[0])
        for posAdd, image_id in enumerate(tagData.images):
            if image_id not in taggedImageIds:
                sql = "INSERT INTO tagmap (image_id, tag_id, pos) VALUES (%s, %s, %s)"
                val = (image_id, tag_id, last_pos+posAdd)
                mycursor.execute(sql, val)
            else:
                pass  # maybe reorder them

        self.db.commit()
        mycursor.close()

    def remove_image_from_tag(self, tagData: TagData):
        """
        Works the same as tagImages just in reverse
        :param TagData
        Removes specified images from the tag (edits table tagmap and removes all connections between the two)
       :return: returns {error: False}
        """

        mycursor = self.db.cursor()
        tag_id = self.find_tag_id(tagData.tag)
        if tag_id == None:
            return {"error": "Tag doesn't exist"}

        for image_id in tagData.images:
            sql = f"""
                DELETE FROM tagmap
                    WHERE tag_id={tag_id}
                    AND image_id={image_id};
                    """
            mycursor.execute(sql)
        self.db.commit()
        mycursor.close()
        return {"error": False}

    def get_tags_starting_with_pattern(self, pattern: str):
        """
        autocomplete string
        :param tagStart: String tag should start with
        Returns at most 5 values starting with the specified String tagStart in the table tag ordered alphabetically
        :return {"error": False, "tags": [tag1,tag2,...]}
        """
        mycursor = self.db.cursor()
        return get_tags_starting_with(mycursor, pattern)

    """
    Function used for changing tagName from oldTagname to newTagName in the table tag
    """
    def change_tag_name(self, oldTagName, newTagName):
        try:
            mycursor = self.db.cursor()
            sql = """UPDATE tag
                SET tname=%s
                WHERE tname=%s AND tag_id>0
                """  # tag_id>0 has to be called,
            # since safe update mode is enabled for the project and it isn't rly necessary here to select the tag with it's id
            mycursor.execute(sql, (newTagName, oldTagName,))
            self.db.commit()

        except Exception as e:
            return {"error": e}
        finally:
            mycursor.close()

    def set_new_rand_seed(self):
        self.randId = randint(0, 1000000)

    # reordering Images within Tag
    # TODO add different modes
    def reorder_images(self, idShip, idDestination, mode, tagname):
        mycursor = self.db.cursor()

        # drag Ship in front of destination
        sql = f"CALL dragInFrontOfOtherImage({idShip}, {idDestination}, '{tagname}')"
        val = (idShip, idDestination, tagname)
        mycursor.callproc('dragInFrontOfOtherImage',
                          args=(idShip, idDestination, tagname))

        self.db.commit()
        mycursor.close()
