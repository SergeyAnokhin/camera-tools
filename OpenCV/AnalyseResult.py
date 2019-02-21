import json

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

class ContourAnalyseResult:
    area = 0
    profile_proportion =  0.0
    center_coordinate = []
    direction: float

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

    def __repr__(self):
        self.objects = self.GetAllObjectsLabels()
        # dict = self.__dict__.copy()
        # dict['images'] = self.images.toString()
        # dict['directions'] = self.directions.toString()
        return json.dumps(self.__dict__, default= self.dumper, indent=4)

    def dumper(self, obj):
        print("JSON : ", type(obj))
        try:
            return obj.toJSON()
        except:
            return obj.__dict__

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
