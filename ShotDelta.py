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

        areas = [str(cv2.contourArea(c)) for c in self.Contours]
        totalArea = sum(cv2.contourArea(c) for c in self.Contours)

        print('D= Contours found : {}. Total contours area : {}'.format(
            len(self.Contours), totalArea))
        print('D= Contours area: ', ", ".join(areas))
        return self.Contours

    def DrawContours(self, shot: Shot):
        self.GetCountours()
        cv2.drawContours(shot.image_contours,
                         self.Contours, -1, (0, 255, 255), 1)
        for c in self.Contours[0:2]:
            area = int(cv2.contourArea(c) / 100)
            print('Contour: {}'.format(area))

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(shot.image_contours, (x, y),
                          (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(shot.image_contours, str(
                area), (x, y-3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    def MagnifyMotion(self, shot: Shot):
        self.GetCountours()
        if len(self.Contours) == 0:
            return

        counts = 1
        margin = 5
        zoom = 2

        for c in self.Contours[0:counts]:
            (x, y, w, h) = cv2.boundingRect(c)
            img = shot.image_color
            motion_area = img[y:(y+h), x:(x+w)]
            img_xmax = len(img[0])
            img_ymax = len(img)
            motion_area = cv2.resize(
                motion_area, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
            y_max = img_ymax-margin
            y_min = y_max - zoom*h
            x_max = img_xmax-margin
            x_min = x_max - zoom*w
            shot.image_contours[y_min:y_max, x_min:x_max] = motion_area
            cv2.rectangle(shot.image_contours, (x_min, y_min),
                          (x_max, y_max), (127, 127, 127), 2)
