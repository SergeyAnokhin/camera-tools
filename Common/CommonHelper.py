# -*- coding: utf-8 -*-
import datetime, re, json, os, pytz, subprocess, sys, coloredlogs, logging, html
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
        progress = "◼️" * int(round(current / total * maxLenth))
        rest = "◻️" * int(round((1 - current / total) * maxLenth))
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

    def installColoredLog(self, log: logging.Logger):
        coloredlogs.DEFAULT_DATE_FORMAT = '%H:%M:%S'
        coloredlogs.CAN_USE_BOLD_FONT = True
        coloredlogs.DEFAULT_FIELD_STYLES = {
            'asctime': {'color': 'green'}, 
            'hostname': {'color': 'black'}, 
            'levelname': {'color': 'magenta', 'bold': True, 'underline': True}, 
            'name': {'color': 'blue'}, 
            'programname': {'color': 'cyan'}
        }
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            'critical': {'color': 'red', 'bold': True, 'background': 'black'}, 
            'debug': {'color': 1, 'bold': True}, 
            'error': {'color': 'red'}, 
            'info': {'color': 'black', 'faint': True}, 
            'warning': {'color': 'yellow'},
            'notice': {'color': 'magenta'}, 
            'spam': {'color': 'green', 'faint': True}, 
            'success': {'color': 'green', 'bold': True}, 
            'verbose': {'color': 'blue'}, 
        }
        coloredlogs.COLOREDLOGS_LEVEL_STYLES='spam=22;debug=1;verbose=34;notice=220;warning=202;success=118,bold;error=124;critical=background=red'
        coloredlogs.install(logger=log, isatty=True)
        coloredlogs.install(level=logging.DEBUG, fmt='%(asctime)s|%(levelname)-.3s|%(name)-.10s: %(message)s', isatty=True)

    mapDict = {
        "question": "&#x2754;",
        "person": "&#x1F6B9;",
        "handbug": "&#x1F4BC;",
        "car": "&#x1F697;",
        "suitcase": "&#x1F9F3;",
        "fire hydrant": "&#x1F9EF;",
        "skateboard": "&#x1F6F9;",
        "dog": "&#x1F415;",
        "bear": "&#x1F43B;",
        "bird": "&#x1F426;",
        "cat": "&#x1F408;",
        "bicycle": "&#x1F6B2;",
        "handbag": "&#x1F45C;",
    }

    def MapToConsoleEmojiOrEmpty(self, label: str, empty = " "):
        if label in self.mapDict:
            return html.unescape(self.mapDict[label]) + " "
        else:
            return empty

    def MapToHtmlEmojiOrEmpty(self, label: str):
        if label in self.mapDict:
            return self.mapDict[label]
        else:
            return ""

    def MapToHtmlEmojiText(self, label: str):
        for old, new in self.mapDict.items():
            label = label.replace(old, new)
        return label
        #return mapDict[label] if label in mapDict else label

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        #print("type: ", type(obj))
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)
