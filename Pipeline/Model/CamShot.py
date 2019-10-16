import re, datetime, cv2, os
from copy import copy, deepcopy
from Common.CommonHelper import CommonHelper
from Pipeline.Model.FileImage import FileImage

class CamShot(FileImage):
    
    def __init__(self, *args, **kwargs):
        self.helper = CommonHelper()
        return super().__init__(*args, **kwargs)

    def GetDatetime(self, is_raise_exception = True):
        return self.helper.get_datetime(self.filename, is_raise_exception)

    def GrayImage(self):
        return cv2.cvtColor(self.GetImage(), cv2.COLOR_BGR2GRAY)

    def Clone(self):
        copy = CamShot(self.fullname)
        if len(self.image):
            copy.image = deepcopy(self.image)
        return copy

