import cv2, logging
import numpy as np
import pprint as pp
from asq import query
from Pipeline.Model.PipelineShot import PipelineShot
from Processors.Processor import Processor
from Processors.Tracking.TrackingBox import TrackingBox
from Common.CommonHelper import CommonHelper

class TrackingProcessor(Processor):

    def __init__(self, isDebug=False):
        super().__init__("TRAC")
        self.boxes_last = []
        self.helper = CommonHelper()
        self.isDebug = isDebug

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        super().ProcessShot(pShot, pShots)
        meta = self.CreateMetadata(pShot)
        shot = pShot.Shot
        prevPShot = self.GetPreviousShot(pShot, pShots)
        if not prevPShot:
            return
        boxes_last = list(self.GetTrackingBoxes(prevPShot))
        boxes = self.GetTrackingBoxes(pShot)
        # if 'YOLO' not in pShot.Metadata or 'areas' not in pShot.Metadata['YOLO']:
        #     self.log.warning("No data on YOLO analysis found. Ignore tracking analysys")
        #     return
        # summary = pShot.Metadata['YOLO']['areas']
        
        # for box_index, box_data in enumerate(summary):

        #     box = TrackingBox(box_data)
        #     box.ExtractBox(shot.GetImage())
        #     box.id = box_index
        for box in boxes:

            #boxes_current.append(box)
            bestMatched:TrackingBox = box.CompareBox(boxes_last)
            if bestMatched != None:
                #cv2.line(shot.image,bestMatched.center,box.center,(255,0,0),3)
                box.DrawLine(shot.GetImage(), bestMatched)
                box.id = bestMatched.id
                meta[box.id] = {}
                meta[box.id]['distance'] = int(box.Distance(bestMatched))
                meta[box.id]['angle'] = int(box.angle(bestMatched))
                if self.isDebug:
                    meta[box.id]['center'] = box.GetCenter()

            box.DrawStartPoint(shot.GetImage())

        #self.boxes_last = boxes_current

    def GetPreviousShot(self, pShot: PipelineShot, pShots: []) -> PipelineShot:
        index = pShot.Index
        if index == 0:
            return None
        return query(pShots) \
            .first_or_default(lambda p: p.Index == index + 1, None)

    def GetTrackingBoxes(self, pShot):
        if 'YOLO' not in pShot.Metadata or 'areas' not in pShot.Metadata['YOLO']:
            self.log.warning("No data on YOLO analysis found. Ignore tracking analysys")
            return
        summary = pShot.Metadata['YOLO']['areas']
        
        for box_index, box_data in enumerate(summary):

            box = TrackingBox(box_data)
            box.ExtractBox(pShot.Shot.GetImage())
            box.id = box_index
            yield box