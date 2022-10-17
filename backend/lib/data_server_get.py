from lib.models import SortMode


def get_image_list_from_server(mycursor, offset: int, count: int, sort_mode: int, tag: str, random_id: int):
    returnDict = {"error": False, "sort_mode": sort_mode, "data": {}}
    data = {}
    sqlLimit = " LIMIT %s " + f"OFFSET %s"
    order_mode = ""
    if tag == None:
        sql = "SELECT * FROM image "

        if sort_mode == SortMode.DATE:
            order_mode = "ORDER BY id"  # was ORDER BY time_created before
        elif sort_mode == SortMode.DATE_REVERSE:
            order_mode = "ORDER BY id DESC"  # descending was ORDER BY time_created DESC before
        elif sort_mode == SortMode.RANDOM:
            order_mode = "ORDER BY RAND("+str(random_id)+")"
        else:
            order_mode = "ORDER BY id"

        mycursor.execute(sql+order_mode+sqlLimit, (count, offset,))
        rows = mycursor.fetchall()
        for count, row in enumerate(rows):
            data[count] = row
        returnDict["data"] = data

    else:  # for tagged search
        if sort_mode == SortMode.POSITION:
            order_mode = "it.pos"
        elif sort_mode == SortMode.DATE:
            order_mode = "img.id"  # was ORDER BY time_created before
        elif sort_mode == SortMode.DATE_REVERSE:
            order_mode = "img.id DESC"  # descending was ORDER BY time_created DESC before
        elif sort_mode == SortMode.RANDOM:
            order_mode = "RAND("+str(random_id)+")"
        else:
            order_mode = "it.pos"

        data = {}

        if(tag == "_" or tag == " "):  # get all untagged images
            if(order_mode == "it.pos"):  # TODO find better way 2 fix
                order_mode = "img.id DESC"
            sql = f"""
            SELECT img.*
            FROM image img
            WHERE img.id not in (SELECT image_id FROM tagmap) 
            ORDER BY {order_mode} 
            """
            mycursor.execute(sql+sqlLimit)
        else:  # get images with tag
            sql = f"""
            SELECT img.*
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
        returnDict["data"] = data

    mycursor.close()
    return returnDict


def get_tag_list_from_server(mycursor, offset: str, count: str, sort_mode: int, random_id: int, tag: str = ""):
    returnDict = {"error": False, "sort_mode": sort_mode, "data": {}}
    data = {}

    if sort_mode == SortMode.POSITION:
        order_mode = "t.tname ASC"
    elif sort_mode == SortMode.DATE:
        order_mode = "tm.id"  # was ORDER BY time_created before
    elif sort_mode == SortMode.DATE_REVERSE:
        order_mode = "tm.id DESC"  # descending was ORDER BY time_created DESC before
    elif sort_mode == SortMode.RANDOM:
        order_mode = "RAND("+str(random_id)+")"
    elif sort_mode == SortMode.POPULARITY:
        order_mode = "tmGrouped.size DESC"

        # was this previously but since query times were getting slow now just looking at highest pos
        #order_mode = "(SELECT COUNT(tag_id) FROM tagmap WHERE tag_id=tm.tag_id GROUP BY tag_id) DESC"
    else:
        order_mode = "tmGrouped.size DESC"

    if tag == "":
        sql = f"""
        SELECT  img.file_path, img.id, tm.tag_id, t.tname
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
        SELECT  img.file_path, img.id, tm.tag_id, t.tname
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

    returnDict["data"] = data
    mycursor.close()
    return returnDict


def get_tags_starting_with(mycursor,  tag_start: str):
    """
        autocomplete string
        :param tag_start: String tag should start with
        Returns at most 5 values starting with the specified String tag_start in the table tag ordered alphabetically
        :return {"error": False, "tags": [tag1,tag2,...]}
        """
    tag_startLen = str(len(tag_start))
    # gets first 5 tags starting with tag_start
    sql = f"""SELECT tname 
            FROM tag 
            WHERE left(tname,%s)=%s
            ORDER BY tname LIMIT 5;
        """
    mycursor.execute(sql, (tag_startLen, tag_start,))
    tags = {"error": False, "tags": []}
    for row in mycursor:
        tags["tags"].append(row[0])  # row 0 is the tag
    mycursor.close()
    return tags
