import cv2, logging
import numpy as np
import pprint as pp
from Pipeline.Model.CamShot import CamShot
from Pipeline.Model.ProcessingResult import ProcessingResult
from Common.CommonHelper import CommonHelper

class DiffCamShot:

    def __init__(self, shot: CamShot, shots):
        self.Result = ProcessingResult()
        self.Result.Summary = {}
        self.log = logging.getLogger("PROC:DIFF")
        self.shot = shot
        self.shots = shots

    def Process(self):
        self.log.debug(f"==={self.shot.filename}===")
        self.Result.Shot = self.shot.Copy();

        mask1 = self.DiffMask(self.shots[0])
        mask2 = self.DiffMask(self.shots[1])

        maskMean = self.Merge(mask1, mask2, lambda x, y: x//2 + y//2) # difference on any shot
        cntsMean = self.ContoursByMask(maskMean)
        self.DrawContours(self.Result.Shot, cntsMean, color=(0, 180, 180))

        maskMin = self.Merge(mask1, mask2, lambda x, y: min(x, y)) # only difference with two others
        cntsMin = self.ContoursByMask(maskMin, 'Diff')
        self.DrawContours(self.Result.Shot, cntsMin, thickness=2)
        self.DrawBoxes(self.Result.Shot, cntsMin)

        return self.Result

    def RemoveZones(self, image):
        image_timestamp = image[:22, :230]
        image[:22, :230] = 0 # remove timestamp
        return image

    def ContoursByMask(self, mask, summaryName = ''):
        cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)
        areas = [cv2.contourArea(c) for c in cnts]
        areasStr = [str(a) for a in areas]
        totalArea = sum(cv2.contourArea(c) for c in cnts)
        if summaryName != '':
            self.Result.Summary[summaryName] = {}
            self.Result.Summary[summaryName]['TotalArea'] = totalArea
            self.Result.Summary[summaryName]['Areas'] = areas
        self.log.debug(f'Contours {summaryName}: {len(cnts)}. Total contours area : {totalArea} ({", ".join(areasStr)})')
        return cnts

    def Merge(self, arr1, arr2, func):
        result = arr1.copy()
        for x in range(len(arr1)):
            for y in range(len(arr1[x])):
                result[x, y] = func(arr1[x, y], arr2[x, y])
        return result


    def DrawContours(self, shot, contours, color=(0, 255, 255), thickness=1):
        cv2.drawContours(shot.image, contours, -1, color, thickness)

    def DrawBoxes(self, shot, contours):
        boxes = []
        for c in contours[0:2]:
            area = int(cv2.contourArea(c))
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(shot.image, (x, y), (x + w, y + h), (0, 255, 0), 1, 8)
            cv2.putText(shot.image, str(area // 100), (x, y-3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
            boxes.append({  
                'profile_proportion': round(h/w,2),
                'center': [x + w//2, y + h//2],
                'area': area
            })

        self.Result.Summary['boxes'] = boxes

    def DiffMask(self, withshot):
        image1 = self.RemoveZones(self.shot.GrayImage())
        image2 = self.RemoveZones(withshot.GrayImage())

        absdiff     = cv2.absdiff(image1, image2)
        gausian     = cv2.GaussianBlur(absdiff, (5, 5), 0)
        _, thresh   = cv2.threshold(gausian, 40, 255, cv2.THRESH_BINARY)
        dilate      = cv2.dilate(thresh, np.ones((10, 10), np.uint8))
        return dilate

class DiffContoursProcessor:
    
    def __init__(self):
        self.Shots = []
        self.log = logging.getLogger("PROC:DIFF")

    def Process(self):
        results = []
        size = len(self.Shots)
        for i in range(size):
            # next_index = (i+1) if i < (size-1) else 0  ### => (0,1) (1,2) (2,0)
            current = self.Shots[i]
            others = self.Shots.copy()
            others.remove(current)
            diff = DiffCamShot(current, others)
            result = diff.Process()
            results.append(result)
        return results
