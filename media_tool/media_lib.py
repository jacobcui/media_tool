"""
Library for media files.
"""
import os
from datetime import datetime

import PIL
import pyheif
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image


class ConvertionError(Exception):
    pass


def get_photo_taken_date(image_path: str) -> datetime:
    """Retrieves taken date as YYYY_MM_DD format."""

    taken_date = None
    try:
        with Image.open(image_path) as img:
            exif = img._getexif()
            if exif:
                taken_date = exif[0x9003]  # "DateTimeOriginal"
    except (PIL.UnidentifiedImageError, KeyError, AttributeError, FileNotFoundError):
        return None

    return datetime.strptime(taken_date, "%Y:%m:%d %H:%M:%S") if taken_date else None


def get_movie_taken_date(file_path: str) -> datetime:
    """Retrieves taken date as YYYY_MM_DD format."""

    taken_date = None
    try:
        with open(file_path, "rb") as _fh:
            parser = createParser(_fh)
            metadata = extractMetadata(parser)
            taken_date = metadata.get("creation_date")

    except (AttributeError, FileNotFoundError):
        return None

    return taken_date


def convert_heic_to_jpeg_ext(
    heic_path: str, jpeg_path: str = None, remove_original: bool = False
) -> str:
    """Convert heic to jpeg using pyheif."""

    if not jpeg_path:
        jpeg_path = heic_path.lower().replace("heic", "JPG")

    heif_file = pyheif.read(heic_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.save(jpeg_path, format="JPEG")

    if remove_original:
        os.remove(heic_path)

    return jpeg_path


def convert_heic_to_jpeg(
    heic_path: str, jpeg_path: str = None, remove_original: bool = False
) -> str:
    """Convert heic to jpeg."""

    if not jpeg_path:
        jpeg_path = heic_path.lower().replace("heic", "JPG")

    try:
        # Open the HEIC file
        heic_image = Image.open(heic_path)

        # Save as JPEG
        heic_image.convert("RGB").save(jpeg_path, "JPEG")

        if remove_original:
            os.remove(heic_path)

        return jpeg_path

    except Exception:
        try:
            return convert_heic_to_jpeg_ext(
                heic_path=heic_path,
                jpeg_path=jpeg_path,
                remove_original=remove_original,
            )
        except Exception as e:
            raise ConvertionError(e)
