import json


class SecretConfig:
    usermane: str
    password: str
    filename = 'secret_config.json'
        
    def fromJsonFile(self):
        with open(self.filename, "r") as read_file:
            self.__dict__ = json.load(read_file)

    def fromJson(self, json_dump):
        self.__dict__ = json.loads(json_dump)

    def toJson(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return 'CONFIG: = {}'.format(self.filename)