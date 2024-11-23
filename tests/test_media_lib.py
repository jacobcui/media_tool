import os
from datetime import datetime

import media_lib
import pytest


@pytest.mark.parametrize(
    "filename,expected_date_string",
    [
        ("IMG_0259.HEIC", datetime(2023, 1, 7, 19, 51, 2)),
        ("IMG_0975.PNG", None),
        ("IMG_5485.JPG", datetime(2023, 11, 9, 21, 4, 13)),
    ],
)
def test_get_photo_taken_date(media_dir, filename, expected_date_string):
    photo_path = os.path.join(media_dir, filename)

    assert expected_date_string == media_lib.get_photo_taken_date(photo_path)


@pytest.mark.parametrize(
    "filename,expected_date_string",
    [
        ("IMG_0967.MOV", datetime(2023, 1, 3, 12, 31, 20)),
        ("IMG_8091.MP4", None),
        ("IMG_6114.MOV", datetime(2023, 8, 11, 23, 57, 36)),
    ],
)
def test_get_movie_taken_date(media_dir, filename, expected_date_string):
    movie_path = os.path.join(media_dir, filename)

    assert expected_date_string == media_lib.get_movie_taken_date(movie_path)
