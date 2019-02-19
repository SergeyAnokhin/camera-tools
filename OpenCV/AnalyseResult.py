class ImageAnalyseResult:
    contours = []
    objects = []

class ContourAnalyseResult:
    area: int
    profile_proportion: float
    center_coordinate = []
    direction: float

class ObjectAnalyseResult(ContourAnalyseResult):
    label: str
    confidence: int

class AnalyseResult:
    images = []
    objects: str
    day_time: str # night, day, mi_day
    is_false_alert: bool
    directions = []

    def GetMailBody(self):
        return "(log must be here)"

    def GetMailSubject(self):
        return "(subject must be here)"
