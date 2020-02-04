from .defaults import *

USED_SETTINGS = __name__

ELASTICSEARCH_HOST = 'elasticsearch:9200'
# 172.19.0.2:9300
CAMERA_LIVE_PATH = "/camera-OpenCV-data"
CAMERA_ARCHIVE_PATH = "/camera-OpenCV-data"
HASSIO_PATH = "/code/temp/hassio"

print("Import settings: " + USED_SETTINGS)
