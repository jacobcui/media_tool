import os

import pytest

_MEDIA_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def media_dir():
    return _MEDIA_DIR
