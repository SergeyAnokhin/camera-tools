import numpy as np
from Pipeline.Model.CamShot import CamShot


class YoloDetection:

    def __init__(self, detection, shot: CamShot):
        self.detection = detection
        self.shot = shot
        (self.ImageHeight, self.ImageWidth) = self.shot.GetImage().shape[:2]

    def GetClassId(self):
        scores = self.detection[5:]
        return np.argmax(scores)

    def GetConfidence(self):
        scores = self.detection[5:]
        classID = np.argmax(scores)
        return float(scores[classID])

    def GetBoxCoordinates(self):
        # scale the bounding box coordinates back relative to the
        # size of the image, keeping in mind that YOLO actually
        # returns the center (x, y)-coordinates of the bounding
        # box followed by the boxes' width and height
        box = self.detection[0:4] \
                    * np.array([self.ImageWidth, self.ImageHeight, self.ImageWidth, self.ImageHeight])
        (centerX, centerY, width, height) = box.astype("int")

        # use the center (x, y)-coordinates to derive the top and
        # and left corner of the bounding box
        x = int(centerX - (width / 2))
        y = int(centerY - (height / 2))
        return (x, y, int(width), int(height))


