import json
from asq import query

class SecretConfig:
    filename = 'configs/secret.json'

    def __init__(self):
        self.gmail_username = ""
        self.gmail_password = ""
        self.image_id_decode_key = ""
        self.camera_tools_host = ""
        self.networks = []

    def fromJsonFile(self):
        with open(self.filename, "r") as read_file:
            self.__dict__ = json.load(read_file)

    def fromJson(self, json_dump):
        self.__dict__ = json.loads(json_dump)

    def toJson(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return 'CONFIG: = {}'.format(self.filename)

    def GetNetworkConfig(self, network: str):
        return query(self.networks) \
            .where(lambda n: network in n['network']) \
            .first_or_default(None)
