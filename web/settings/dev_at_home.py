### from winserver
from .defaults import *

USED_SETTINGS = __name__
DEBUG = True
ELASTICSEARCH_HOST = '192.168.1.31:3192'
CAMERA_LIVE_PATH = "\\\\diskstation\\Camera"
CAMERA_ARCHIVE_PATH = "\\\\diskstation"
HASSIO_PATH = "\\\\hassio\\config\\www\snapshot"
DNS_HOST = "192.168.1.1"

print("Import settings: " + USED_SETTINGS)
