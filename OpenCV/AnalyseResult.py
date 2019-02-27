import json
from datetime import datetime
import decimal
from Common.CommonHelper import CommonHelper, ComplexEncoder


class ImageAnalyseResult:

    def __init__(self):
        self.contours = []
        self.objects = []

    def __repr__(self):
        #return json.dumps(self.__dict__, indent=4)
        return "Objects: {}".format(self.GetObjectsStr())

    def GetObjectsStr(self):
        result = ""
        for obj in self.objects:
            result += " {}:{:.3f}".format(obj.label, obj.confidence)
        return result

    def reprJSON(self):
        d = self.__dict__
        d["contours"] = self.contours
        d["objects"] = self.objects
        return d


class ContourAnalyseResult:

    def __init__(self):
        self.area = 0
        self.profile_proportion =  0.0
        self.center_coordinate = []
        self.direction = 0.0

    def reprJSON(self):
        d = self.__dict__
        return d

    def __repr__(self):
        return "a:{}/p:{}@[{center[0]},{center[1]}]".format(self.area, self.profile_proportion, center =self.center_coordinate)

class ObjectAnalyseResult(ContourAnalyseResult):
    label = ""
    confidence = 0.0

    def __repr__(self):
        return "[Object] __{}__: {:.3f}".format(self.label, self.confidence)

class AnalyseResult:

    def __init__(self):
        self.images = []
        self.objects: str
        self.day_time: str # night, day, mi_day
        self.is_false_alert: bool
        self.directions = []
        self.processing_time = f"{datetime.now():%Y-%m-%d %H:%M:%S}"

    def toJson(self):
        return json.dumps(self.reprJSON(), cls=ComplexEncoder, indent=4)

    def __repr__(self):
        self.objects = self.GetAllObjectsLabels()
        return self.objects

    def reprJSON(self):
        d = self.__dict__
        d["objects"] = self.GetAllObjectsLabels()
        d["images"] = self.images
        d["directions"] = self.directions
        return d

    def GetAllObjectsLabels(self):
        labels = set()
        for img in self.images:
            for obj in img.objects:
                labels.add(obj.label)
        return " ".join(labels)

    def GetMailBody(self):
        return self.toJson()

    def GetMailSubject(self, camera: str, time: datetime):
        self.objects = self.GetAllObjectsLabels()
        return "{} @{:%H:%M} | {}".format(camera, time, self.objects)
