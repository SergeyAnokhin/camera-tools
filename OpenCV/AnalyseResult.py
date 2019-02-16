class AnalyseResult:
    images: []

class ImageAnalyseResult:
    contours: ContourAnalyseResult[]
    objects: []

class ContourAnalyseResult:
    area: int
    center_coordinate: []

class ObjectAnalyseResult:
    label: str
    center_coordinate: []
    confidence: int