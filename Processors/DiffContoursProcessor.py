import cv2, logging
import numpy as np
from Pipeline.Model.CamShot import CamShot

class DiffCamShot:

    def __init__(self, shot: CamShot, shots):
        self.log = logging.getLogger("PROC:DIFF")
        self.shot = shot
        self.shots = shots

    def Process(self):
        deltaShot = CamShot()
        mask1 = self.DiffMask(self.shots[0])
        mask2 = self.DiffMask(self.shots[1])
        mask = mask1.copy()
        for x in range(len(mask1)):
            for y in range(len(mask1[x])):
                mask[x, y] = min(mask1[x, y], mask2[x, y])

        deltaShot.SetImage(mask)
        return deltaShot

    def DiffMask(self, withshot):
        absdiff     = cv2.absdiff(self.shot.GrayImage(), withshot.GrayImage())
        gausian     = cv2.GaussianBlur(absdiff, (5, 5), 0)
        _, thresh   = cv2.threshold(gausian, 40, 255, cv2.THRESH_BINARY)
        dilate      = cv2.dilate(thresh, np.ones((10, 10), np.uint8))
        return dilate

class DiffContoursProcessor:
    
    def __init__(self):
        self.Shots = []
        self.log = logging.getLogger("PROC:DIFF")

    def Process(self):
        deltas = []
        size = len(self.Shots)
        for i in range(size):
            # next_index = (i+1) if i < (size-1) else 0  ### => (0,1) (1,2) (2,0)
            current = self.Shots[i]
            others = self.Shots.copy()
            others.remove(current)
            diff = DiffCamShot(current, others)
            delta = diff.Process()
            deltas.append(delta)
        return deltas

    # def CalcCountours(self):
    #     self.Delta = cv2.absdiff(self.shot1.image, self.shot2.image)
    #     self.GaussianBlur = cv2.GaussianBlur(self.Delta, (5, 5), 0)
    #     ret, self.Threshold = cv2.threshold(
    #         self.GaussianBlur, 40, 255, cv2.THRESH_BINARY)
    #     self.Dilate = cv2.dilate(self.Threshold, np.ones((10, 10), np.uint8))
    #     cnts, h = cv2.findContours(
    #         self.Dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #     self.Contours = sorted(
    #         cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)

    #     # areas = [str(cv2.contourArea(c)) for c in self.Contours]
    #     # totalArea = sum(cv2.contourArea(c) for c in self.Contours)
    #     # print('D= Contours found : {}. Total contours area : {}'.format(
    #     #     len(self.Contours), totalArea))
    #     # print('D= Contours area: ', ", ".join(areas))
    #     return self.Contours
