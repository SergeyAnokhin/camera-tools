### from winserver
from .defaults import *

USED_SETTINGS = __name__
DEBUG = True
ELASTICSEARCH_HOST = 'elasticsearch:9200'
# 172.19.0.2:9300
CAMERA_LIVE_PATH = "/mnt/Camera"
CAMERA_ARCHIVE_PATH = "/mnt"
HASSIO_PATH = "/mnt/Hassio/www/snapshot"
DNS_HOST = "192.168.1.1"

print("Import settings: " + USED_SETTINGS)
