from lib.models import SortMode


def get_image_list_from_server(mycursor, offset: int, count: int, sortMode: int, tag: str, randId: int):
    returnDict = {"error": False, "sortMode": sortMode, "data": {}}
    data = {}
    sqlLimit = " LIMIT %s " + f"OFFSET %s"
    orderMode = ""
    if tag == None:
        sql = "SELECT * FROM image "

        if sortMode == SortMode.DATE:
            orderMode = "ORDER BY id"  # was ORDER BY time_created before
        elif sortMode == SortMode.DATE_REVERSE:
            orderMode = "ORDER BY id DESC"  # descending was ORDER BY time_created DESC before
        elif sortMode == SortMode.RANDOM:
            orderMode = "ORDER BY RAND("+str(randId)+")"
        else:
            orderMode = "ORDER BY id"

        mycursor.execute(sql+orderMode+sqlLimit, (count, offset,))
        rows = mycursor.fetchall()
        for count, row in enumerate(rows):
            data[count] = row
        returnDict["data"] = data

    else:  # for tagged search
        if sortMode == SortMode.POSITION:
            orderMode = "it.pos"
        elif sortMode == SortMode.DATE:
            orderMode = "img.id"  # was ORDER BY time_created before
        elif sortMode == SortMode.DATE_REVERSE:
            orderMode = "img.id DESC"  # descending was ORDER BY time_created DESC before
        elif sortMode == SortMode.RANDOM:
            orderMode = "RAND("+str(randId)+")"
        else:
            orderMode = "it.pos"

        data = {}

        if(tag == "_" or tag == " "):  # get all untagged images
            if(orderMode == "it.pos"):  # TODO find better way 2 fix
                orderMode = "img.id DESC"
            sql = f"""
            SELECT img.*
            FROM image img
            WHERE img.id not in (SELECT image_id FROM tagmap) 
            ORDER BY {orderMode} 
            """
            mycursor.execute(sql+sqlLimit)
        else:  # get images with tag
            sql = f"""
            SELECT img.*
            FROM tagmap it, image img, tag t
            WHERE it.tag_id = t.tag_id
            AND t.tname = %s
            AND img.id = it.image_id
            ORDER BY {orderMode}
            """
            mycursor.execute(sql+sqlLimit, (tag, count, offset,))
        rows = mycursor.fetchall()
        for count, row in enumerate(rows):
            data[count] = row
        returnDict["data"] = data

    mycursor.close()
    return returnDict


def get_tag_list_from_server(mycursor, offset: str, count: str, sortMode: int, randId: int, tag: str = ""):
    returnDict = {"error": False, "sortMode": sortMode, "data": {}}
    data = {}

    if sortMode == SortMode.POSITION:
        orderMode = "t.tname ASC"
    elif sortMode == SortMode.DATE:
        orderMode = "tm.id"  # was ORDER BY time_created before
    elif sortMode == SortMode.DATE_REVERSE:
        orderMode = "tm.id DESC"  # descending was ORDER BY time_created DESC before
    elif sortMode == SortMode.RANDOM:
        orderMode = "RAND("+str(randId)+")"
    elif sortMode == SortMode.POPULARITY:
        orderMode = "tmGrouped.size DESC"

        # was this previously but since query times were getting slow now just looking at highest pos
        #orderMode = "(SELECT COUNT(tag_id) FROM tagmap WHERE tag_id=tm.tag_id GROUP BY tag_id) DESC"
    else:
        orderMode = "tmGrouped.size DESC"

    if tag == "":
        sql = f"""
        SELECT  img.file_path, img.id, tm.tag_id, t.tname
        FROM (SELECT MIN(pos) AS pos, tag_id, MAX(pos) as size FROM tagmap GROUP BY tag_id) tmGrouped,
            tag t, image img, tagmap tm
        WHERE tmGrouped.tag_id=tm.tag_id
            AND tmGrouped.tag_id=t.tag_id 
            AND tm.pos=tmGrouped.pos
            AND img.id=tm.image_id 
            ORDER BY {orderMode}
            LIMIT %s
            OFFSET %s
        """
        mycursor.execute(sql, (count, offset,))
    else:
        sql = f"""
        SELECT  img.file_path, img.id, tm.tag_id, t.tname
        FROM (SELECT MIN(pos) AS pos, tag_id, MAX(pos) as size FROM tagmap GROUP BY tag_id) tmGrouped,
            tag t, image img, tagmap tm
        WHERE left(t.tname, %s)=%s
            AND tmGrouped.tag_id=tm.tag_id
            AND tmGrouped.tag_id=t.tag_id 
            AND tm.pos=tmGrouped.pos
            AND img.id=tm.image_id 
            ORDER BY {orderMode}
            LIMIT {count}
            OFFSET {offset}
        """
        mycursor.execute(sql, (len(tag), tag, ))

    rows = mycursor.fetchall()
    for count, row in enumerate(rows):
        data[count] = row

    returnDict["data"] = data
    mycursor.close()
    return returnDict


def get_tags_starting_with(mycursor,  tagStart: str):
    """
        autocomplete string
        :param tagStart: String tag should start with
        Returns at most 5 values starting with the specified String tagStart in the table tag ordered alphabetically
        :return {"error": False, "tags": [tag1,tag2,...]}
        """
    tagStartLen = str(len(tagStart))
    # gets first 5 tags starting with tagStart
    sql = f"""SELECT tname 
            FROM tag 
            WHERE left(tname,%s)=%s
            ORDER BY tname LIMIT 5;
        """
    mycursor.execute(sql, (tagStartLen, tagStart,))
    tags = {"error": False, "tags": []}
    for row in mycursor:
        tags["tags"].append(row[0])  # row 0 is the tag
    mycursor.close()
    return tags
