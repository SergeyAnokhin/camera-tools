import cv2
import Shot
import numpy as np


class ShotDelta:
    Contours: any

    def __init__(self, shot1: Shot, shot2: Shot):
        self.shot1 = shot1
        self.shot2 = shot2
        self.Delta = cv2.absdiff(self.shot1.image, self.shot2.image)

    def CalcCountours(self):
        self.GaussianBlur = cv2.GaussianBlur(self.Delta, (5, 5), 0)
        ret, self.Threshold = cv2.threshold(
            self.GaussianBlur, 40, 255, cv2.THRESH_BINARY)
        self.Dilate = cv2.dilate(self.Threshold, np.ones((10, 10), np.uint8))
        cnts, h = cv2.findContours(
            self.Dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Contours = sorted(
            cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)

        areas = [str(cv2.contourArea(c)) for c in self.Contours]
        totalArea = sum(cv2.contourArea(c) for c in self.Contours)

        # print('D= Contours found : {}. Total contours area : {}'.format(
        #     len(self.Contours), totalArea))
        # print('D= Contours area: ', ", ".join(areas))
        return self.Contours
