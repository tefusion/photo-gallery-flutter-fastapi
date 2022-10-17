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

    def __init__(self, p_database: str):
        """
        Creates connection to sqlServer
        """
        self.directoryPath = "./Files/Received/"
        self.thumbnailPath = "./Files/square/"
        self.random_id: int = randint(0, 1000000)
        load_dotenv()
        PASSWORD = os.getenv("DB_PASSWORD")
        self.db = mysql.connector.connect(
            host="localhost",
            database=p_database,
            user="root",
            password=PASSWORD
        )

    def return_image(self, image_path):
        """
        param image_path: str
        returns specified file at Path
        """
        return FileResponse(self.directoryPath+image_path)

    def return_thumbnail(self, image_path: str, size: int):
        """
        same as returnImage, just returns smaller square cut from it
        """
        if os.path.isfile(self.thumbnailPath+image_path):  # if thumbnail exists return it
            thumbnail = FileResponse(self.thumbnailPath+image_path)
        else:  # if thumbnail doesn't exist create it, this was necessary at the start since thumbnails weren't saved previously
            # can be removed in a future version
            self.create_thumbnail(image_path, size)
            thumbnail = FileResponse(self.thumbnailPath+image_path)

        return thumbnail

    def create_thumbnail(self, image_path: str, size: int):
        """
        param image_path: str
        param size: int

        Uses PILLOW/PIL.Image to cut the middle out of the image and resize it to the size to have a thumbnail in square format
        """
        im = Image.open(self.directoryPath+image_path)
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

        thumbnail.save(self.thumbnailPath+image_path)
        # this is the option of not saving the image, but sending it directly
        # img_byte_arr = io.BytesIO()
        # thumbnail.save(img_byte_arr, format='PNG')
        # return StreamingResponse(iter([img_byte_arr.getvalue()]), media_type='image/png')

    def get_image_list(self, offset: int, count: int, sort_mode: int, tag: str):
        """
        param offset: str (but has to actually be an int, since all gets passed in sql as a str int values already passed as str)
        param count: str: Limit count
        param sort_mode: int see sort_mode enum
        param tag: str: for future use of retrieving only tags starting with this pattern
        """
        try:
            mycursor = self.db.cursor(dictionary=True)
        except:
            self.__init__()
            mycursor = self.db.cursor(dictionary=True)
        return get_image_list_from_server(mycursor, offset=offset, count=count, sort_mode=sort_mode, tag=tag, random_id=self.random_id)

    def get_tag_list(self, offset: int, count: int, sort_mode: int, tag: str = ""):
        """
        params: offset, count, sort_mode
        gets tagList with thumbnails from sql server
        """
        try:
            mycursor = self.db.cursor(dictionary=True)
        except:
            self.__init__()
            mycursor = self.db.cursor(dictionary=True)
        return get_tag_list_from_server(mycursor, offset=offset, count=count, sort_mode=sort_mode, random_id=self.random_id, tag=tag)

    def add_to_image_table(self, file_name, fileData: FileData, tag=""):
        mycursor = self.db.cursor()

        if tag != "" and tag != " ":
            tag_data = TagData(tag=tag, images=[])

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO image (title, description, file_path, time_created) VALUES (%s, %s, %s, %s)"
        val = (fileData.title, fileData.description, file_name, now)
        mycursor.execute(sql, val)
        if tag != "" and tag != " ":
            tag_data.images.append(mycursor.lastrowid)
        self.db.commit()
        mycursor.close()
        if tag != "" and tag != " ":
            self.tagImages(tag_data=tag_data)

    # for multiple images:

    async def upload_multiple_images(self, multi_file_data: MultiFileData):

        file_names = []
        for file in multi_file_data.files:
            fileNameArr = file.filename.split(".")
        # new generated file name with same file extension
            if multi_file_data.compressed == False:
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
            file_names, multi_file_data.title, multi_file_data.description, multi_file_data.tag)

    def add_multiple_images_to_table(self, file_names, title, description, tag):
        try:
            mycursor = self.db.cursor()
        except Exception as e:
            self.__init__()
            mycursor = self.db.cursor(dictionary=True)

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if tag != "" and tag != " ":
            tag_data = TagData(tag=tag, images=[])
        for file_name in file_names:
            sql = "INSERT INTO image (title, description, file_path, time_created) VALUES (%s, %s, %s, %s)"
            val = (title, description, file_name, now)
            mycursor.execute(sql, val)
            if tag != "" and tag != " ":
                tag_data.images.append(mycursor.lastrowid)
        self.db.commit()
        mycursor.close()
        if tag != "" and tag != " ":
            self.tag_images(tag_data=tag_data)

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

    def tag_images(self, tag_data: TagData):
        """
        Input Value TagData
        Adds images in tag_data.images to tag_data.tag in tagmap
        """
        mycursor = self.db.cursor()
        # make better way to do this .-.
        # this is just a quick check if the tag even exists
        # if it doesn't just add the first image to it so it actually exists
        tag_id = self.find_tag_id(tag_data.tag)
        if tag_id == None:
            self.add_new_tag(tag_data.tag)
            tag_id = self.find_tag_id(tag_data.tag)

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
        for posAdd, image_id in enumerate(tag_data.images):
            if image_id not in taggedImageIds:
                sql = "INSERT INTO tagmap (image_id, tag_id, pos) VALUES (%s, %s, %s)"
                val = (image_id, tag_id, last_pos+posAdd)
                mycursor.execute(sql, val)
            else:
                pass  # maybe reorder them

        self.db.commit()
        mycursor.close()

    def remove_image_from_tag(self, tag_data: TagData):
        """
        Works the same as tagImages just in reverse
        :param TagData
        Removes specified images from the tag (edits table tagmap and removes all connections between the two)
       :return: returns {error: False}
        """

        mycursor = self.db.cursor()
        tag_id = self.find_tag_id(tag_data.tag)
        if tag_id == None:
            return {"error": "Tag doesn't exist"}

        for image_id in tag_data.images:
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

    def change_tag_name(self, old_tag_name, new_tag_name):
        """
        Function used for changing tagName from oldTagname to new_tag_name in the table tag
        """
        try:
            mycursor = self.db.cursor()
            sql = """UPDATE tag
            SET tname=%s
            WHERE tname=%s AND tag_id>0
            """  # tag_id>0 has to be called,
            # since safe update mode is enabled for the project and it isn't rly necessary here to select the tag with it's id
            mycursor.execute(sql, (new_tag_name, old_tag_name,))
            self.db.commit()

        except Exception as e:
            return {"error": e}
        finally:
            mycursor.close()

    def set_new_rand_seed(self):
        self.random_id = randint(0, 1000000)

    # reordering Images within Tag
    # TODO add different modes
    def reorder_images(self, id_ship, id_destination, mode, tagname):
        mycursor = self.db.cursor()

        # drag Ship in front of destination
        sql = f"CALL dragInFrontOfOtherImage({id_ship}, {id_destination}, '{tagname}')"
        val = (id_ship, id_destination, tagname)
        mycursor.callproc('dragInFrontOfOtherImage',
                          args=(id_ship, id_destination, tagname))

        self.db.commit()
        mycursor.close()
