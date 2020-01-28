from .defaults import *

USED_SETTINGS = "test"

ELASTICSEARCH_HOST = None
CAMERA_LIVE_PATH = "C:\\Src\\temp\\CameraArchive"
CAMERA_ARCHIVE_PATH = "C:\\Src\\camera-OpenCV-data\\Camera"
HASSIO_PATH = "temp"

ELASTICSEARCH_DSL={
    'default': {
        'hosts': '192.168.99.100:3192'
    },
}

print("Import settings: " + USED_SETTINGS)
