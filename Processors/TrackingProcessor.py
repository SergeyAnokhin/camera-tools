import cv2, logging, asq
import numpy as np
import pprint as pp
import pandas as pd
from tabulate import tabulate
from asq import query
from Pipeline.Model.PipelineShot import PipelineShot
from Processors.PipelineShotProcessor import PipelineShotProcessor
from Processors.Tracking.TrackingBox import TrackingBox
from Common.CommonHelper import CommonHelper

# TODO : extract background for better matching 
class TrackingProcessor(PipelineShotProcessor):
    LastID = -1

    def __init__(self, isDebug=False):
        super().__init__("TRAC")
        self.boxes_last = []
        self.helper = CommonHelper()
        self.isDebug = isDebug

    def Process(self, context: dict):
        TrackingProcessor.LastID = 0
        super().Process(context)

    def GetNewObjectId(self) -> int:
        TrackingProcessor.LastID += 1
        return TrackingProcessor.LastID

    def ProcessItem(self, pShot: PipelineShot, ctx: dict):
        super().ProcessItem(pShot, ctx)
        pShots = ctx['data']
        meta = self.CreateMetadata(pShot)
        shot = pShot.Shot
        boxes = list(self.GetTrackingBoxes(pShot))

        prevPShot = self.GetPreviousShot(pShot, pShots)
        if not prevPShot:
            for box in boxes:
                meta[box.id] = {}
                box.object_id = self.GetNewObjectId()
                meta[box.id]['object_id'] = box.object_id
                self.log.debug(f"Draw box: {box}")
                box.DrawStartPoint(shot.GetImage())
            return
        boxes_last = list(self.GetTrackingBoxes(prevPShot))

        self.MatchObjects(boxes, boxes_last)
        self.DefineNewObjects(boxes, pShot)

        for box in boxes:
            # bestMatched:TrackingBox = box.CompareBox(boxes_last)
            bestMatched:TrackingBox = query(boxes_last) \
                .first_or_default(None, lambda b: b.object_id == box.object_id)
            if bestMatched == None:
                self.log.debug(f" Best matchid box not found, draw ignore: Box: B{box.id}")
                continue
            #cv2.line(shot.image,bestMatched.center,box.center,(255,0,0),3)
            self.log.debug(f"Draw box track: {box.id} ({box.GetCenter()})  matched:{bestMatched.id} ({bestMatched.GetCenter()})")
            self.log.debug(f"Draw line: {bestMatched.GetCenter()} => {box.GetCenter()}")
            box.DrawLine(shot.GetImage(), bestMatched)
            box.DrawStartPoint(shot.GetImage())
            #box.id = bestMatched.id
            meta[box.id] = {}
            meta[box.id]['object_id'] = box.object_id
            meta[box.id]['distance'] = int(box.Distance(bestMatched))
            meta[box.id]['angle'] = int(box.angle(bestMatched))
            if self.isDebug:
                meta[box.id]['center'] = box.GetCenter()

    def DefineNewObjects(self, boxes: [], pShot: PipelineShot):
        # this box not matched. when len(prev_boxes) < len(boxes). New Object ?
        for b in asq.query(boxes) \
                .where(lambda b: b.object_id == None):
            b.object_id = self.GetNewObjectId()
            b.DrawStartPoint(pShot.Shot.GetImage())

    def CreateCorrMatrix(self, boxes: [], boxes_prev: []):
        coeffs = np.zeros((len(boxes), len(boxes_prev))) # coeff matrix: rows x columns

        for i, b in enumerate(boxes):
            for j, b_prev in enumerate(boxes_prev):
                coeffs[i][j] = b_prev.GetMatchingCoeff(b)

        #with np.printoptions(precision=3, suppress=True):
        #    self.log.debug(f"Matching Coeffs matrix: \n{pd.DataFrame(coeffs)}")
        headers = [b.ToStringShort() for b in boxes_prev]
        headers.insert(0, "Curr\\Prev") # for first column with boxes IDs
        rows = [b.id for b in boxes]
        matrix = np.c_[rows, coeffs]
        self.log.debug(f"Matching Coeffs matrix: \n" 
            + f"{tabulate(matrix, headers, tablefmt='orgtbl', floatfmt='.3f')}")
        return coeffs

    def MatchObjects(self, boxes: [], boxes_prev: []):
        coeffs = self.CreateCorrMatrix(boxes, boxes_prev)

        for _ in boxes: # loop len(boxes) times
            max = np.amax(coeffs)
            if max == 0: 
                break # no more matching
            pos = np.where(coeffs == max)
            i = pos[0][0]
            j = pos[1][0]
            box = boxes[i]
            box_prev = boxes_prev[j]
            self.log.debug(f"Max: '{max:.3f}' position: {i}x{j}. Write Object_ID: {box_prev}=>{box}")
            box.object_id = box_prev.object_id # match
            coeffs[i, :] = 0.0
            coeffs[:, j] = 0.0

    def GetPreviousShot(self, pShot: PipelineShot, pShots: []) -> PipelineShot:
        index = pShot.Index
        if index == 0:
            return None
        return query(pShots) \
            .first_or_default(None, lambda p: p.Index == index - 1) # 

    def GetTrackingBoxes(self, pShot: PipelineShot) -> []:
        if 'YOLO' not in pShot.Metadata or 'areas' not in pShot.Metadata['YOLO']:
            self.log.warning("No data on YOLO analysis found. Ignore tracking analysys")
            return
        yolo = pShot.Metadata['YOLO']['areas']
        meta = self.CreateMetadata(pShot)
        
        for box_data in yolo:
            box = TrackingBox(box_data)
            box.ExtractBox(pShot.Shot.GetImage())
            if box.id in meta and 'object_id' in meta[box.id]:
                box.object_id = meta[box.id]['object_id']
            yield box