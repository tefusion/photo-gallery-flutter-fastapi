import os
from sqlite3 import Cursor
from debugpy import connect

from dotenv import load_dotenv
import mysql.connector

TABLES = {}
TABLES['image'] = """
    CREATE TABLE `image` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(20),
  `description` varchar(100),
  `uuid` char(36) NOT NULL,
  `type` varchar(10) NOT NULL,
  `time_created` datetime,
  PRIMARY KEY (`id`)
);
    """

TABLES['tag'] = """
    CREATE TABLE `tag` (
    `tag_id` int(11) NOT NULL AUTO_INCREMENT,
    `tname` varchar(20) NOT NULL,
    PRIMARY KEY (`tag_id`)
);
    """

TABLES['tagmap'] = """
    CREATE TABLE `tagmap` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `image_id` int(11) NOT NULL,
    `tag_id` int(11) NOT NULL,
    `pos` int(11) NOT NULL,
    PRIMARY KEY (`id`)
);
"""


class DatabaseConnector:
    """
    Just an easy class to ensure closing connections. Only allows one cursor.
    """

    def __init__(self) -> None:
        load_dotenv("app/.env")
        self.cxn = mysql.connector.connect(
            host="localhost",
            database="test_images",
            user="root",
            password=os.getenv("DB_PASSWORD")
        )

        self.my_cursor = self.cxn.cursor()

    def __del__(self) -> None:
        self.my_cursor.close()
        self.cxn.close()

    def get_cursor(self):
        return self.my_cursor


def init_tables():
    """
    See init.sql. Basically runs that here to have empty tables for testing for the database test_images
    """

    try:
        connector = DatabaseConnector()
    except:
        print(
            "Could not create DatabaseConnector, likely test_images database not created or .env failed to load.")
        return

    my_cursor = connector.get_cursor()
    for table_name, table_creation in TABLES.items():
        # drop table from previous test (if exists)
        my_cursor.execute("DROP TABLE IF EXISTS " + table_name)

        # create new table:
        my_cursor.execute(table_creation)


init_tables()
