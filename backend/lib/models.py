from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import Optional, List

from enum import Enum


class FileData(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file: UploadFile = File(...)


class MultiFileData(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    files: List[UploadFile] = File(...)
    tag: Optional[str] = None
    compressed: Optional[bool] = False


class TagData(BaseModel):
    tag: str = None
    images: List[int] = []


class SortMode(Enum):
    DATE = 1
    DATE_REVERSE = 2
    POSITION = 3
    RANDOM = 4
    POPULARITY = 5


def convert_sort_mode(input_string):
    if input_string == None:
        return SortMode.DATE
    sort_mode_str = input_string.upper()
    if sort_mode_str == "DATE":
        return SortMode.DATE
    elif sort_mode_str in ["MOST_RECENT", "DATE_REVERSE"]:
        return SortMode.DATE_REVERSE
    elif sort_mode_str == "POPULARITY":
        return SortMode.POPULARITY
    elif sort_mode_str == "POSITION":
        return SortMode.POSITION
    elif sort_mode_str == "RANDOM":
        return SortMode.RANDOM
    else:
        return SortMode.DATE
