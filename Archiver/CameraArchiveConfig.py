import json, os
from Common.SecretConfig import SecretConfig
from Common.CommonHelper import CommonHelper

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
    networkConfig = {}

    def __init__(self):
        self.ignore_dir = []
        self.secretConfig = SecretConfig()
        self.secretConfig.fromJsonFile()
        self.Init()

    def Init(self):
        if not self.networkConfig:
            self.networkConfig = self.helper.GetNetworkConfig()

    def fromJsonFile(self, filename: str):
        with open(filename, "r") as read_file:
            self.__dict__ = json.load(read_file)
        if not hasattr(self, 'ignore_dir'):
            self.ignore_dir = []
        self.Init()

    def fromJson(self, json_dump):
        self.__dict__ = json.loads(json_dump)
        if not hasattr(self, 'ignore_dir'):
            self.ignore_dir = []
        self.Init()

    def toJson(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return 'CONFIG: {}: = {}'.format(self.camera, self.path_from)

    def pathFrom(self):
        return os.path.join(self.networkConfig['camera_live_path'], self.path_from)

    def pathTo(self):
        return os.path.join(self.networkConfig['camera_archive_path'], self.path_to)