# Media Tool
Batch rename photos, videos, and convert heic to jpeg. Add date to filename.

Usage:
```
python media_tool/media_tool.py --directory  <folder_with_media>
```

## Install
```
poetry env use 3.12
sudo apt-get install libheif-dev
```

pyheif has issue with python 3.13, so use 3.12 for now.


## Test:
```
PYTHONPATH=media_tool pytest tests
```
