import os
import cv2
import logging
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from OpenCV.Shot import Shot
from OpenCV.ShotDelta import ShotDelta
from OpenCV.YoloContext import YoloContext
from OpenCV.AnalyseResult import AnalyseResult, ImageAnalyseResult, ContourAnalyseResult, ObjectAnalyseResult


class ThreeShots:
    shot1: Shot
    shot2: Shot
    shot3: Shot
    delta12: ShotDelta
    delta23: ShotDelta
    delta31: ShotDelta
    yoloContext: YoloContext
    yoloResults = []

    def FromDir(self, dir: str):
        shots = ThreeShots()
        shots.log = logging.getLogger("3SHOTS")
        files = os.listdir(dir)

        shots.shot1 = Shot.FromFile(None, os.path.join(dir, files[0]))
        shots.shot2 = Shot.FromFile(None, os.path.join(dir, files[1]))
        shots.shot3 = Shot.FromFile(None, os.path.join(dir, files[2]))

        shots.delta12 = ShotDelta(shots.shot1, shots.shot2)
        shots.delta23 = ShotDelta(shots.shot2, shots.shot3)
        shots.delta31 = ShotDelta(shots.shot3, shots.shot1)

        return shots

    def Analyse(self):
        self.yoloContext.ProcessItem(self.shot1)
        self.yoloContext.ProcessItem(self.shot2)
        self.yoloContext.ProcessItem(self.shot3)

        self.CalcContours()

        self.shot1.DrawContours()
        self.shot2.DrawContours()
        self.shot3.DrawContours()

        self.shot1.MagnifyMotion()
        self.shot2.MagnifyMotion()
        self.shot3.MagnifyMotion()

        self.CreateWindow()

        plt.subplot(self.gs1[2])
        self.shot1.show_plt()
        plt.subplot(self.gs1[5])
        self.shot3.show_plt()
        plt.subplot(self.gs1[:2, :2])
        self.shot2.show_plt()

        result = AnalyseResult()
        result.images.append(self.shot1.imageAnalyseResult)
        result.images.append(self.shot2.imageAnalyseResult)
        result.images.append(self.shot3.imageAnalyseResult)
        result.is_false_alert = False
        result.objects = "TBD"
        return result

    def CalcContours(self):
        self.delta12.CalcCountours()
        self.delta23.CalcCountours()
        self.delta31.CalcCountours()

        #print('S= Shot1 Contours')
        self.shot1.Contours = self.removeEmptyContours(
            self.delta12, True, False, True)
        #print('S= Shot2 Contours')
        self.shot2.Contours = self.removeEmptyContours(
            self.delta12, True, True, False)
        #print('S= Shot3 Contours')
        self.shot3.Contours = self.removeEmptyContours(
            self.delta23, False, True, True)

        self.shot1.CalcContoursAnalyseResult()
        self.shot2.CalcContoursAnalyseResult()
        self.shot3.CalcContoursAnalyseResult()

    def removeEmptyContours(self, delta: ShotDelta, diff12=True, diff23=False, diff31=True):
        new_contours = []
        for c in delta.Contours:
            (x, y, w, h) = cv2.boundingRect(c)
            rect12 = self.delta12.Threshold[y:(y+h), x:(x+w)]
            rect23 = self.delta23.Threshold[y:(y+h), x:(x+w)]
            rect31 = self.delta31.Threshold[y:(y+h), x:(x+w)]
            max12 = np.amax(rect12)
            max23 = np.amax(rect23)
            max31 = np.amax(rect31)
            # print('Max delta Contour ({}): 1-2:{} 2-3:{} 3-1:{}'
            #     .format(cv2.contourArea(c), max12, max23, max31))
            if ((max12 > 0 and diff12) or (max12 >= 0 and not diff12)) \
                and \
                ((max23 > 0 and diff23) or (max23 >= 0 and not diff23)) \
                and \
                    ((max31 > 0 and diff31) or (max31 >= 0 and not diff31)):
                new_contours.append(c)
                # if max12 > 0 and max23 > 0 and max31 > 0:
                #     print('!!! Motion in same place : velocity = 0')
            # else:
            #     print('remove contour')

        return new_contours

    def CreateWindow(self):
        plt.figure(figsize=(12, 6.025))
        self.gs1 = gridspec.GridSpec(2, 3, left=0, right=1, top=1,
                                     bottom=0, wspace=0, hspace=0)

    def Show(self):
        # plt.tight_layout()
        plt.margins(0)
        plt.show()

    def Save(self, filenamePattern:  str):
        self.output_filename = filenamePattern.format(self.shot1.datetime)
        self.log.info("Save figure to: " + self.output_filename)
        plt.savefig(self.output_filename, bbox_inches='tight', pad_inches=0)
