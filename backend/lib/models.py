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


def convert_sort_mode(inputString):
    if inputString == None:
        return SortMode.DATE
    sortModeStr = inputString.upper()
    if sortModeStr == "DATE":
        return SortMode.DATE
    elif sortModeStr in ["MOST_RECENT", "DATE_REVERSE"]:
        return SortMode.DATE_REVERSE
    elif sortModeStr == "POPULARITY":
        return SortMode.POPULARITY
    elif sortModeStr == "POSITION":
        return SortMode.POSITION
    elif sortModeStr == "RANDOM":
        return SortMode.RANDOM
    else:
        return SortMode.DATE
