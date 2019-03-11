import re, datetime
from Pipeline.Model.FileCamShot import FileCamShot

class CamShot(FileCamShot):
    
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def GetDatetime(self):
        re_groups = re.search("(20\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)", 
            self.filename)
        if not re_groups:
            print('Cant parse datetime in : {}'.format(input))
            raise ValueError('Cant parse datetime in file : {}'.format(input))
        year = int(re_groups.group(1))
        month = int(re_groups.group(2))
        day = int(re_groups.group(3))
        hour = int(re_groups.group(4))
        minute = int(re_groups.group(5))
        seconds = int(re_groups.group(6))
        return datetime.datetime(year, month, day, hour, minute, seconds)
