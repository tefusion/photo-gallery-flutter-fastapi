from fastapi.responses import FileResponse, StreamingResponse
from fastapi import File, Response, UploadFile

import os
# import PIL
from PIL import Image

import uuid

import mysql.connector
import datetime

from dotenv import load_dotenv

from random import randint

from app.models import *
from app.file_storage_handler import FileStorageHandler


THUMBNAIL_SIZE = 200


class ImageServer:
    """
    Handles everything related to database
    """

    def __init__(self, p_database: str, folder_path: str):
        """Creates connection to sqlServer

        Args:
            p_database (str): data_base name like image
            folder_path (str): path where square and Received folder are like ./Files
        """
        self.random_id: int = randint(0, 1000000)
        self.file_handler = FileStorageHandler(folder_path)
        load_dotenv()
        PASSWORD = os.getenv("DB_PASSWORD")
        self.db = mysql.connector.connect(
            host="localhost",
            database=p_database,
            user="root",
            password=PASSWORD
        )

    def return_image(self, image_path: str) -> FileResponse:
        """returns specified file at Path
        Args:
            image_path (str): just image name

        Returns:
            FileResponse: image
        """
        full_image_path = self.file_handler.get_image_path(image_path)
        if full_image_path != "":
            return FileResponse(full_image_path, 200)
        else:
            failed_response = Response(None, 404)
            return failed_response

    def return_thumbnail(self, image_path: str) -> FileResponse:
        """
        same as returnImage, just returns smaller square cut from it
        """
        thumbnail_path = self.file_handler.get_thumbnail_path(image_path)
        if thumbnail_path != "":
            return FileResponse(thumbnail_path, 200)
        else:
            return Response(None, 404)

    def get_image_list(self, offset: int, count: int, sort_mode: int, tag: str) -> dict:
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
        return_dict = {"sort_mode": sort_mode, "data": {}}
        data = {}
        sqlLimit = " LIMIT %s " + f"OFFSET %s"
        order_mode = ""
        if tag == None:
            sql = "SELECT title, description, uuid, type, time_created FROM image "

            if sort_mode == SortMode.DATE:
                order_mode = "ORDER BY id"  # was ORDER BY time_created before
            elif sort_mode == SortMode.DATE_REVERSE:
                order_mode = "ORDER BY id DESC"  # descending was ORDER BY time_created DESC before
            elif sort_mode == SortMode.RANDOM:
                order_mode = "ORDER BY RAND("+str(self.random_id)+")"
            else:
                order_mode = "ORDER BY id"

            mycursor.execute(sql+order_mode+sqlLimit, (count, offset,))
            rows = mycursor.fetchall()
            for count, row in enumerate(rows):
                data[count] = row
            return_dict["data"] = data

        else:  # for tagged search
            if sort_mode == SortMode.POSITION:
                order_mode = "it.pos"
            elif sort_mode == SortMode.DATE:
                order_mode = "img.id"  # was ORDER BY time_created before
            elif sort_mode == SortMode.DATE_REVERSE:
                order_mode = "img.id DESC"  # descending was ORDER BY time_created DESC before
            elif sort_mode == SortMode.RANDOM:
                order_mode = "RAND("+str(self.random_id)+")"
            else:
                order_mode = "it.pos"

            data = {}

            if (tag == "_" or tag == " "):  # get all untagged images
                if (order_mode == "it.pos"):
                    order_mode = "img.id DESC"
                sql = f"""
                SELECT img.title, img.description, img.uuid, img.type, img.time_created
                FROM image img
                WHERE img.id not in (SELECT image_id FROM tagmap) 
                ORDER BY {order_mode} 
                """
                mycursor.execute(sql+sqlLimit)
            else:  # get images with tag
                sql = f"""
                SELECT img.title, img.description, img.uuid, img.type, img.time_created
                FROM tagmap it, image img, tag t
                WHERE it.tag_id = t.tag_id
                AND t.tname = %s
                AND img.id = it.image_id
                ORDER BY {order_mode}
                """
                mycursor.execute(sql+sqlLimit, (tag, count, offset,))
            rows = mycursor.fetchall()
            for count, row in enumerate(rows):
                data[count] = row
            return_dict["data"] = data

        mycursor.close()
        return return_dict

    def get_tag_list(self, offset: int, count: int, sort_mode: int, tag: str = "") -> dict:
        """
        params: offset, count, sort_mode
        gets tagList with thumbnails from sql server
        """
        try:
            mycursor = self.db.cursor(dictionary=True)
        except:
            self.__init__()
            mycursor = self.db.cursor(dictionary=True)

        return_dict = {"sort_mode": sort_mode, "data": {}}
        data = {}

        if sort_mode == SortMode.POSITION:
            order_mode = "t.tname ASC"
        elif sort_mode == SortMode.DATE:
            order_mode = "tm.id"  # was ORDER BY time_created before
        elif sort_mode == SortMode.DATE_REVERSE:
            order_mode = "tm.id DESC"  # descending was ORDER BY time_created DESC before
        elif sort_mode == SortMode.RANDOM:
            order_mode = "RAND("+str(self.random_id)+")"
        elif sort_mode == SortMode.POPULARITY:
            order_mode = "tmGrouped.size DESC"

            # was this previously but since query times were getting slow now just looking at highest pos
            #order_mode = "(SELECT COUNT(tag_id) FROM tagmap WHERE tag_id=tm.tag_id GROUP BY tag_id) DESC"
        else:
            order_mode = "tmGrouped.size DESC"

        if tag == "":
            sql = f"""
            SELECT  img.uuid, img.type, tm.tag_id, t.tname
            FROM (SELECT MIN(pos) AS pos, tag_id, MAX(pos) as size FROM tagmap GROUP BY tag_id) tmGrouped,
                tag t, image img, tagmap tm
            WHERE tmGrouped.tag_id=tm.tag_id
                AND tmGrouped.tag_id=t.tag_id 
                AND tm.pos=tmGrouped.pos
                AND img.id=tm.image_id 
                ORDER BY {order_mode}
                LIMIT %s
                OFFSET %s
            """
            mycursor.execute(sql, (count, offset,))
        else:
            sql = f"""
            SELECT  img.uuid, img.type, tm.tag_id, t.tname
            FROM (SELECT MIN(pos) AS pos, tag_id, MAX(pos) as size FROM tagmap GROUP BY tag_id) tmGrouped,
                tag t, image img, tagmap tm
            WHERE left(t.tname, %s)=%s
                AND tmGrouped.tag_id=tm.tag_id
                AND tmGrouped.tag_id=t.tag_id 
                AND tm.pos=tmGrouped.pos
                AND img.id=tm.image_id 
                ORDER BY {order_mode}
                LIMIT {count}
                OFFSET {offset}
            """
            mycursor.execute(sql, (len(tag), tag, ))

        rows = mycursor.fetchall()
        for count, row in enumerate(rows):
            data[count] = row

        return_dict["data"] = data
        mycursor.close()
        return return_dict

    def add_image_to_table(self, file_uuid: str, file_type: str, title: str, description: str) -> int:
        """Call after saving file for both image and thumbnail

        Args:
            file_name (str):
            title (str): 
            description (str): 
            tag (str, optional):. Defaults to "".
        """
        mycursor = self.db.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO image (uuid, type, title, description, time_created) VALUES (%s, %s, %s, %s, %s)"
        val = (file_uuid, file_type, title, description, now)
        mycursor.execute(sql, val)

        image_id = mycursor.lastrowid
        self.db.commit()
        mycursor.close()
        return image_id

    # for multiple images:
    async def upload_multiple_images(self, multi_file_data: MultiFileData):
        file_names = []
        for file in multi_file_data.files:
            fileNameArr = file.filename.split(".")
        # new generated file name with same file extension
            if multi_file_data.compressed == False:
                new_filename = str(uuid.uuid4())+"." + \
                    fileNameArr[len(fileNameArr)-1]
                self.file_handler.save_file(file.file, new_filename)
                self.file_handler.create_thumbnail(
                    new_filename, THUMBNAIL_SIZE)
                file_names.append(new_filename)
            else:  # in compressed mode all images saved as jpeg
                new_filename = str(uuid.uuid4())+".jpg"
                self.file_handler.save_file_compressed(file.file, new_filename)
                self.file_handler.create_thumbnail(
                    new_filename, THUMBNAIL_SIZE)
                file_names.append(new_filename)

        self.add_multiple_images_to_table(
            file_names, multi_file_data.title, multi_file_data.description, multi_file_data.tag)

        return {"images": file_names}

    def add_multiple_images_to_table(self, file_names, title, description, tag):
        if tag != "" and tag != " ":
            tag_data = TagData(tag=tag, images=[])
        for file_name in file_names:
            file_uuid: str = file_name.split(".")[0]
            file_type: str = file_name.split(".")[1]
            image_id = self.add_image_to_table(
                file_uuid, file_type, title, description)
            if tag != "" and tag != " ":
                tag_data.images.append(file_uuid)

        if tag != "" and tag != " ":
            self.tag_images(tag_data=tag_data)

    async def delete_image(self, image_uuid: str):
        mycursor = self.db.cursor()
        mycursor.execute(
            "SELECT id, type FROM image WHERE uuid=%s", (image_uuid, ))
        try:
            normal_id = None
            for row in mycursor:
                normal_id = row[0]
                file_type = row[1]

            if normal_id == None:
                return Response(None, 404)

            mycursor.execute("DELETE FROM image WHERE uuid=%s", (image_uuid, ))
            mycursor.execute(
                "DELETE FROM tagmap WHERE image_id=%s", (normal_id,))
            self.db.commit()

            self.file_handler.remove_image(image_uuid+"."+file_type)
            return Response(None, 200)

        except:
            return Response(None, 500)

        finally:
            mycursor.close()

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
        tagged_image_ids = []
        for row in mycursor:
            tagged_image_ids.append(row[0])
        for posAdd, image_uuid in enumerate(tag_data.images):
            image_id = self.get_id_from_uuid(image_uuid)
            if image_id == None:
                continue
            if image_id not in tagged_image_ids:
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
            return {}

        for image_uuid in tag_data.images:
            image_id = self.get_id_from_uuid(image_uuid)
            sql = """
                DELETE FROM tagmap
                    WHERE tag_id=%s
                    AND image_id=%s;
                    """
            mycursor.execute(sql, (tag_id, image_id, ))
        self.db.commit()
        mycursor.close()
        return Response(None, 200)

    def get_tags_starting_with_pattern(self, tag_start: str):
        """
        autocomplete string
        :param tag_start: String tag should start with
        Returns at most 5 values starting with the specified String tagStart in the table tag ordered alphabetically
        :return {"tags": [tag1,tag2,...]}
        """
        mycursor = self.db.cursor()
        tag_start_len = str(len(tag_start))
        # gets first 5 tags starting with tag_start
        sql = f"""SELECT tname 
                FROM tag 
                WHERE left(tname,%s)=%s
                ORDER BY tname LIMIT 5;
            """
        mycursor.execute(sql, (tag_start_len, tag_start,))
        tags = {"tags": []}
        for row in mycursor:
            tags["tags"].append(row[0])  # row 0 is the tag
        mycursor.close()
        return tags

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
            return {}
        finally:
            mycursor.close()

    def set_new_rand_seed(self):
        self.random_id = randint(0, 1000000)

    # reordering Images within Tag
    # TODO add different modes
    def reorder_images(self, uuid_ship: str, uuid_destination: str, mode, tagname):
        id_ship = self.get_id_from_uuid(uuid_ship)
        id_destination = self.get_id_from_uuid(uuid_destination)
        mycursor = self.db.cursor()
        # drag Ship in front of destination
        mycursor.callproc('dragInFrontOfOtherImage',
                          args=(id_ship, id_destination, tagname))

        self.db.commit()
        mycursor.close()
        return Response(None, 200)

    def get_id_from_uuid(self, uuid: str) -> int:
        mycursor = self.db.cursor()
        mycursor.execute(
            "SELECT id FROM image WHERE uuid=%s", (uuid, ))

        row = mycursor.fetchone()
        image_id = None
        mycursor.close()
        if row != None:
            image_id = row[0]
        return image_id
