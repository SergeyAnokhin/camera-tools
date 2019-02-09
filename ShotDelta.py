import cv2
import Shot
import numpy as np


class ShotDelta:
    Contours: any

    def __init__(self, shot1: Shot, shot2: Shot):
        self.shot1 = shot1
        self.shot2 = shot2
        self.Delta = cv2.absdiff(self.shot1.image, self.shot2.image)

    def GetCountours(self):
        self.GaussianBlur = cv2.GaussianBlur(self.Delta, (5, 5), 0)
        ret, self.Threshold = cv2.threshold(
            self.GaussianBlur, 40, 255, cv2.THRESH_BINARY)
        self.Dilate = cv2.dilate(self.Threshold, np.ones((10, 10), np.uint8))
        img, cnts, h = cv2.findContours(
            self.Dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Contours = sorted(
            cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)

        areas = [str(cv2.contourArea(c)) for c in cnts]
        totalArea = sum(cv2.contourArea(c) for c in self.Contours)

        print('D= Contours found : {}. Total contours area : {}'.format(
            len(self.Contours), totalArea))
        print('D= Contours area: ', ", ".join(areas))
        return self.Contours

    def DrawContours(self, shot: Shot):
        self.GetCountours()
        cv2.drawContours(shot.image_color, self.Contours, -1, (0, 255, 255), 1)
        for c in self.Contours[0:2]:
            area = int(cv2.contourArea(c) / 100)
            print('Contour: {}'.format(area))

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(shot.image_color, (x, y),
                          (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(shot.image_color, str(
                area), (x, y-3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
