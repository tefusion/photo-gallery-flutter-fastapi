from ast import Str
from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import Optional, List

from enum import Enum
import inspect
from typing import Type
from pydantic import BaseModel
from fastapi import Form


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls
# Upload models


class FileData(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file: UploadFile = File(...)


@as_form
class MultiFileData(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    files: List[UploadFile] = File(...)
    tag: Optional[str] = None
    compressed: Optional[bool] = False


class TagData(BaseModel):
    tag: str = None
    images: List[str] = []


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


# Response models
class UploadedImagesResponse(BaseModel):
    images: List[str]


class ImageListResponse(BaseModel):
    sort_mode: SortMode
    data: dict


class TagListResponse(BaseModel):
    sort_mode: SortMode
    data: dict
