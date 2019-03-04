import os
import re
import datetime
import pytz
from Common.CommonHelper import CommonHelper


class FileInfo:
    filename: str   # file.jpg
    path: str       # C:\Path\to\file.jpg
    dir: str        # C:\Path\to\

    def __init__(self, full_filename):
        self.helper = CommonHelper()

        self.local = pytz.timezone("Europe/Paris")
        self.path = full_filename
        self.filename = os.path.basename(full_filename)
        self.dir = os.path.dirname(full_filename)

    def get_extension(self):
        _, file_extension = os.path.splitext(self.filename)
        return file_extension.replace('.', '')

    def get_datetime(self):
        re_groups = re.search("(20\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)", 
            self.filename)
        if not re_groups:
            print('Cant parse datetime in file : {}'.format(self.path))
            raise ValueError('Cant parse datetime in file : {}'.format(self.path))
        year = int(re_groups.group(1))
        month = int(re_groups.group(2))
        day = int(re_groups.group(3))
        hour = int(re_groups.group(4))
        minute = int(re_groups.group(5))
        seconds = int(re_groups.group(6))
        return datetime.datetime(year, month, day, hour, minute, seconds)

    def get_datetime_utc(self):
        naive = self.get_datetime()
        local_dt = self.local.localize(naive)
        return local_dt.astimezone(pytz.utc)

    def get_month_id_utc(self):
        return self.get_datetime_utc().strftime('%Y.%m')

    def get_timestamp(self): # 'MDAlarm_20190131-153706'
        return self.get_datetime().strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def get_timestamp_utc(self): # 'MDAlarm_20190131-153706'
        return self.get_datetime_utc().strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def size(self):
        return os.path.getsize(self.path)

    def size_human(self):
        size = self.size()
        return self.helper.size_human(size)

    '''
    //diskstation/CameraArchive/Foscam :
    //diskstation/CameraArchive/Foscam/2016-07-26/record/alarm_20160404_010956.mkv => /2016-07-26/record/alarm_20160404_010956.mkv
    '''
    def get_path_relative(self, dir_base: str):
        return self.path.replace(dir_base, '')

    '''
    //diskstation/CameraArchive/Foscam :
    //diskstation/CameraArchive/Foscam/2016-07-26/record/alarm_20160404_010956.mkv => /2016-07-26/record
    '''
    def get_dir_relative(self, dir_base: str):
        path_relative = self.get_path_relative(dir_base)
        return os.path.dirname(path_relative)
