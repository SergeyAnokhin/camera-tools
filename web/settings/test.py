from .defaults import *

USED_SETTINGS = "test"

ELASTICSEARCH_HOST = None
CAMERA_LIVE_PATH = "C:\\Src\\camera-OpenCV-data\\Camera"
CAMERA_ARCHIVE_PATH = "C:\\Src\\camera-OpenCV-data"
PHOTO_ARCHIVE_PATH = "C:\\Src\\temp"
HASSIO_PATH = "temp"
DNS_ADGUARD_API_QUERY_LOG = "tests/data/dns_adguard_querylog.json"
DNS_HOST = "8.8.8.8"

ELASTICSEARCH_DSL={
    'default': {
        'hosts': '192.168.99.100:3192'
    },
}

print("Import settings: " + USED_SETTINGS)
