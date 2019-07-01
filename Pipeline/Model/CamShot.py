import re, datetime, cv2, os
from copy import copy, deepcopy
from Pipeline.Model.FileImage import FileImage

class CamShot(FileImage):
    
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

    def GetMailAttachmentIndex(self):
        re_groups = re.search("-(\\d)\.", self.filename)
        if not re_groups:
            print('Cant get index in : {}'.format(input))
            raise ValueError('Cant get index in file : {}'.format(input))
        return int(re_groups.group(1))

    def GrayImage(self):
        return cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def Clone(self):
        copy = CamShot(self.fullname)
        if len(self.image) != 0:
            copy.image = deepcopy(self.image)
        return copy

