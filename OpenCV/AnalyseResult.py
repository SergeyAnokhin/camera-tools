class AnalyseResult:
    images: []
    objects: str
    day_time: str # night, day, mi_day

class ImageAnalyseResult:
    contours: []
    objects: []

class ContourAnalyseResult:
    area: int
    center_coordinate: []
    direction: float

class ObjectAnalyseResult(ContourAnalyseResult):
    label: str
    confidence: int
