from .defaults import *

USED_SETTINGS = __name__

ELASTICSEARCH_HOST = None
CAMERA_LIVE_PATH = "C:\\Src\\temp\\CameraArchive"
CAMERA_ARCHIVE_PATH = "C:\\Src\\camera-OpenCV-data\\Camera"
PHOTO_ARCHIVE_PATH = "C:\\Src\\temp"
HASSIO_PATH = None

ELASTICSEARCH_DSL={
    'default': {
        'hosts': '192.168.99.100:3192'
    },
}

print("Import settings: " + USED_SETTINGS)
