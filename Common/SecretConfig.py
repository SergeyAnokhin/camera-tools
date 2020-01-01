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

    def GetNetworkConfig(self, network: str, computername: str, platform: str):
        # for n in self.networks:
        #     print(f'========== Name: {n["name"]} =>')
        #     print(n.get("network")[0])
        #     print(network in n.get("network")[0])
        #     print(f'Network: {network in n.get("network")} / {n.get("network")}')
        #     print(f'Computername: {not n.get("computername") or n.get("computername") == computername}')
        #     print(f'Platform: {not n.get("platform") or n.get("platform") == platform}')

        return query(self.networks) \
            .where(lambda n: network in n.get('network') \
                and (not n.get('computername') or n.get('computername') == computername) \
                and (not n.get('platform') or n.get('platform') == platform)) \
            .first_or_default(None)
