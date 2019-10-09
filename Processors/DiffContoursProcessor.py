import cv2, logging
import numpy as np
import pprint as pp
from Pipeline.Model.CamShot import CamShot
from Pipeline.Model.ProcessingResult import ProcessingResult
from Common.CommonHelper import CommonHelper
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class DiffCamShot:

    def __init__(self):
        # self.Result = ProcessingResult()
        # self.Result.Summary = {}
        self.log = logging.getLogger("PROC:DIFF") # :{shot.filenameWithoutExtension}
        # self.shot = ctx.Shot
        # self.originalShot = ctx.OriginalShot
        # self.originalShots = ctx.OriginalShots
        # self.shots = ctx.Shots
        self.helper = CommonHelper()

    def Process(self, pShot: PipelineShot, others: []):
        #self.Result.Shot = self.originalShot.Copy();
        pShot.Metadata["DIFF"] = {}

        mask1 = self.DiffMask(pShot, others[0])
        mask2 = self.DiffMask(pShot, others[1])

        maskMean = self.Merge(mask1, mask2, lambda x, y: x//2 + y//2) # difference on any shot
        cntsMean = self.ContoursByMask(maskMean, pShot)
        self.DrawContours(pShot.Shot, cntsMean, color=(0, 180, 180))

        maskMin = self.Merge(mask1, mask2, lambda x, y: min(x, y)) # only difference with two others
        cntsMin = self.ContoursByMask(maskMin, pShot, 'Diff')
        self.DrawContours(pShot.Shot, cntsMin, thickness=2)
        self.DrawBoxes(pShot, cntsMin)

    def RemoveZones(self, image):
        #image_timestamp = image[:22, :230]
        image[:22, :230] = 0 # remove timestamp
        return image

    def ContoursByMask(self, mask, pShot, summaryName = ''):
        cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)
        areas = [cv2.contourArea(c) for c in cnts]
        areasStr = [str(a) for a in areas]
        totalArea = sum(cv2.contourArea(c) for c in cnts)
        if summaryName != '':
            pShot.Metadata['DIFF'][summaryName] = {}
            pShot.Metadata['DIFF'][summaryName]['TotalArea'] = totalArea
            pShot.Metadata['DIFF'][summaryName]['Areas'] = areas
        self.log.debug(f'{self.helper.Progress(totalArea, 5e4)} Contours {summaryName}: {len(cnts)}. Total contours area : {totalArea} ({", ".join(areasStr)})')
        return cnts

    def Merge(self, arr1, arr2, func):
        result = arr1.copy()
        for x in range(len(arr1)):
            for y in range(len(arr1[x])):
                result[x, y] = func(arr1[x, y], arr2[x, y])
        return result


    def DrawContours(self, shot, contours, color=(0, 255, 255), thickness=1):
        cv2.drawContours(shot.GetImage(), contours, -1, color, thickness)

    def DrawBoxes(self, pShot: PipelineShot, contours):
        pShot.Metadata['DIFF']['boxes'] = []
        for c in contours[0:2]:
            area = int(cv2.contourArea(c))
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(pShot.Shot.GetImage(), (x, y), (x + w, y + h), (0, 255, 0), 1, 8)
            cv2.putText(pShot.Shot.GetImage(), str(area // 100), (x, y-3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
            pShot.Metadata['DIFF']['boxes'].append({  
                'profile_proportion': round(h/w,2),
                'center': [x + w//2, y + h//2],
                'area': area
            })

    def DiffMask(self, pShot: PipelineShot, other: PipelineShot):
        image1 = self.RemoveZones(pShot.OriginalShot.GrayImage())
        image2 = self.RemoveZones(other.OriginalShot.GrayImage())

        absdiff     = cv2.absdiff(image1, image2)
        gausian     = cv2.GaussianBlur(absdiff, (5, 5), 0)
        _, thresh   = cv2.threshold(gausian, 40, 255, cv2.THRESH_BINARY)
        dilate      = cv2.dilate(thresh, np.ones((10, 10), np.uint8))
        return dilate

class DiffContoursProcessor(Processor):

    def __init__(self):
        super().__init__("DIFF")

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        others = pShots.copy()
        others.remove(pShot)
        super().ProcessShot(pShot, others)
        diff = DiffCamShot()
        return diff.Process(pShot, others)

