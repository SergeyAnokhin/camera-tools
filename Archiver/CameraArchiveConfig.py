import json


class CameraArchiveConfig:
    sensor: {}
    position: {}
    camera: str
    path_from: str
    path_to: str
    ignore_dir: []

    def fromJsonFile(self, filename: str):
        with open(filename, "r") as read_file:
            self.__dict__ = json.load(read_file)

    def fromJson(self, json_dump):
        self.__dict__ = json.loads(json_dump)

    def toJson(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return 'CONFIG: {}: = {}'.format(self.camera, self.path_from)
