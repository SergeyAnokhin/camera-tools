import json, os
from Common.SecretConfig import SecretConfig
from Common.CommonHelper import CommonHelper
from Common.AppSettings import AppSettings

class CameraArchiveConfig:
    sensor: {}
    position: {}
    camera: str
    imap_folder: str
    path_from: str
    path_to: str
    ignore_dir: []
    camera_triggered_interval_sec: int

    helper = CommonHelper()

    def __init__(self):
        self.ignore_dir = []
        self.secretConfig = SecretConfig()
        self.secretConfig.fromJsonFile()

    def fromJsonFile(self, filename: str):
        with open(filename, "r") as read_file:
            self.__dict__ = json.load(read_file)
        if not hasattr(self, 'ignore_dir'):
            self.ignore_dir = []

    def fromJson(self, json_dump):
        self.__dict__ = json.loads(json_dump)
        if not hasattr(self, 'ignore_dir'):
            self.ignore_dir = []

    def toJson(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return 'CONFIG: {}: = {}'.format(self.camera, self.path_from)

    def pathFrom(self):
        return os.path.join(AppSettings.CAMERA_LIVE_PATH, self.path_from)

    def pathTo(self):
        return self.path_to