import re, datetime, cv2, os
from copy import copy, deepcopy
from Pipeline.Model.FileImage import FileImage

class CamShot(FileImage):
    
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def GetDatetime(self):
        pattern = "(20\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)[_-]?(\\d\\d)"

        re_groups_index = re.search(pattern + "[_-](\\d)", self.filename)
        if re_groups_index:
            return self.RegexGroupsToDateTime(re_groups_index, int(re_groups_index.group(7)))

        re_groups = re.search(pattern, self.filename)
        if not re_groups:
            print('Cant parse datetime in : {}'.format(input))
            raise ValueError('Cant parse datetime in file : {}'.format(input))
        return self.RegexGroupsToDateTime(re_groups)

    def RegexGroupsToDateTime(self, re_groups, add_seconds = 0):
        year = int(re_groups.group(1))
        month = int(re_groups.group(2))
        day = int(re_groups.group(3))
        hour = int(re_groups.group(4))
        minute = int(re_groups.group(5))
        seconds = int(re_groups.group(6))
        dt = datetime.datetime(year, month, day, hour, minute, seconds)
        return dt + datetime.timedelta(seconds= add_seconds)

    def GetMailAttachmentIndex(self):
        re_groups = re.search("-(\\d)\.", self.filename)
        if not re_groups:
            print('Cant get index in : {}'.format(input))
            #raise ValueError('Cant get index in file : {}'.format(input))
            return None
        return int(re_groups.group(1))

    def GrayImage(self):
        return cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def Clone(self):
        copy = CamShot(self.fullname)
        if len(self.image) != 0:
            copy.image = deepcopy(self.image)
        return copy

