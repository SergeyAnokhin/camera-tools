import json
import datetime
import decimal
from Common.CommonHelper import CommonHelper


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        print("type: ", type(obj))
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)


class ImageAnalyseResult:
    contours = []
    objects = []

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
    area = 0
    profile_proportion =  0.0
    center_coordinate = []
    direction = 0.0

    def reprJSON(self):
        d = self.__dict__
        return d

class ObjectAnalyseResult(ContourAnalyseResult):
    label = ""
    confidence = 0.0

    def __repr__(self):
        return "[Object] {}:{:.3f}".format(self.label, self.confidence)

class AnalyseResult:
    images = []
    objects: str
    day_time: str # night, day, mi_day
    is_false_alert: bool
    directions = []
    helper = CommonHelper()

    def toJson(self):
        return json.dumps(self.reprJSON(), cls=ComplexEncoder, indent=4)

    def __repr__(self):
        self.objects = self.GetAllObjectsLabels()
        # dict = self.__dict__.copy()
        # dict['images'] = self.images.toString()
        # dict['directions'] = self.directions.toString()
        return json.dumps(self.__dict__, default= self.dumper, indent=4)

    def reprJSON(self):
        d = self.__dict__
        d["images"] = self.images
        return d

    def GetAllObjectsLabels(self):
        labels = []
        for img in self.images:
            for obj in img.objects:
                labels.append(obj.label)
        return " ".join(list(set(labels))) # unique

    def GetMailBody(self):
        return "(log must be here)"

    def GetMailSubject(self):
        return "(subject must be here)"
