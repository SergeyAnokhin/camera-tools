import datetime, re, json, os, pytz, subprocess
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
from cryptography.fernet import Fernet
from Common.SecretConfig import SecretConfig
from math import log2

class CommonHelper:
    network = None
    networkConfig = {}

    def __init__(self):
        self.secretConfig = SecretConfig()
        self.secretConfig.fromJsonFile()
        self.local = pytz.timezone("Europe/Paris")

    def get_datetime(self, input: str, is_raise_exception = True):
        pattern = "(20\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)"

        re_groups_index = re.search(pattern + "[_-](\\d)", input)
        if re_groups_index:
            return self.RegexGroupsToDateTime(re_groups_index, int(re_groups_index.group(7)))

        re_groups = re.search(pattern, input)
        if not re_groups:
            print('Cant parse datetime in : {}'.format(input))
            if is_raise_exception:
                raise ValueError('Cant parse datetime in file : {}'.format(input))
            else:
                return None
        try:
            return self.RegexGroupsToDateTime(re_groups)
        except:
            print(f'ERROR: Parse datetime with {input}')
            return None

    def ToUtcTime(self, dt: datetime):
        local_dt = self.local.localize(dt)
        return local_dt.astimezone(pytz.utc)

    def ToTimeStampStr(self, dt: datetime.datetime):
        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def FromTimeStampStr(self, timestamp: str):
        return datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.000Z')

    def RegexGroupsToDateTime(self, re_groups, add_seconds = 0):
        year = int(re_groups.group(1))
        month = int(re_groups.group(2))
        day = int(re_groups.group(3))
        hour = int(re_groups.group(4))
        minute = int(re_groups.group(5))
        seconds = int(re_groups.group(6))
        dt = datetime.datetime(year, month, day, hour, minute, seconds)
        return dt + datetime.timedelta(seconds= add_seconds)

    def IsImage(self, filename: str):
        return filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png")

    def GetEsCameraArchiveIndex(self, datetimeUtc: datetime.datetime):
        return f"cameraarchive-{datetimeUtc:%Y}"

    def GetEsShotId(self, camera: str, datetimeUtc: datetime.datetime):
        stamp = self.ToTimeStampStr(datetimeUtc)
        return f'{camera}@{stamp}'

    def GetNetworkName(self):
        interface_output = subprocess.check_output("netsh interface show interface").decode("ascii",errors="ignore").lower()
        if 'ethernet' in interface_output and 'connecte' in interface_output:
            return 'ethernet'

        wlan_output = subprocess.check_output("netsh wlan show interfaces").decode("ascii",errors="ignore").lower()
        for line in wlan_output.splitlines():
            if " ssid " in line:
                return line.split(':')[1].strip()
        return 'offline'

    def GetNetworkConfig(self):
        if not CommonHelper.network:
            CommonHelper.network = self.GetNetworkName()
            print('!!! Current network: {CommonHelper.network} !!!')
        if not CommonHelper.networkConfig:
            CommonHelper.networkConfig = self.secretConfig.GetNetworkConfig(self.network)
        return CommonHelper.networkConfig

    def FileNameByDateRange(self, filename: str, start: datetime, seconds: int):
        if not start: #no filters
            return True
        dtFile = self.get_datetime(filename, False)
        if not dtFile:
            return False
        dtMax = start + datetime.timedelta(seconds=seconds)
        return start <= dtFile <=dtMax

    def Show(self, image):
        plt.figure(figsize=(8, 6.025))
        gs1 = gridspec.GridSpec(1, 1, left=0, right=1, top=1,
                                     bottom=0, wspace=0, hspace=0)
        plt.subplot(gs1[0])
        plt.axis("off")
        plt.imshow(image, interpolation="bilinear")
        plt.margins(0)
        plt.show()

    def size_human(self, size):
        _suffixes = ['bytes', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb']
        # determine binary order in steps of size 10 
        # (coerce to int, // still returns a float)
        order = int(log2(size) / 10) if size else 0
        # format file size
        # (.4g results in rounded numbers for exact matches and max 3 decimals, 
        # should never resort to exponent values)
        return '{:.4g} {}'.format(size / (1 << (order * 10)), _suffixes[order])

    def Progress(self, current, total = 1, maxLenth = 20):
        current = current if current <=total else total
        limitChar = "|"
        progress = "#" * int(round(current / total * maxLenth))
        rest = "-" * int(round((1 - current / total) * maxLenth))
        return f'{limitChar}{progress}{rest}{limitChar}'

    def WalkFiles(self, path: str, condition, ignoreDirs: [] = None):
        for root, dirnames, filenames in os.walk(path):
            if ignoreDirs and self.dir_to_ignore(root, ignoreDirs):
                continue
            for filename in filenames:
                if condition(filename):
                    yield os.path.join(root, filename)

    def dir_to_ignore(self, dir: str, ignore_dir: []):
        for dir in ignore_dir:
            if dir in dir:
                return True
        return False

    def CleanFolder(self, path: str, condition = None):
        removed = []
        for filename in os.listdir(path):
            file = os.path.join(path, filename)
            if os.path.isfile(file) and not condition or condition(file):
                os.unlink(file)
                removed.append(file)
        return removed

    def Encode(self, message: str):
        key = self.secretConfig.image_id_decode_key.encode()
        return Fernet(key).encrypt(message.encode()).decode()

    def Decode(self, token: str):
        key = self.secretConfig.image_id_decode_key.encode()
        return Fernet(key).decrypt(token.encode()).decode()

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        #print("type: ", type(obj))
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)
