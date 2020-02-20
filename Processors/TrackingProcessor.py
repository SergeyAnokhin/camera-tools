import cv2, logging
import numpy as np
import pprint as pp
import pandas as pd
from tabulate import tabulate
from asq import query
from Pipeline.Model.PipelineShot import PipelineShot
from Processors.PipelineShotProcessor import PipelineShotProcessor
from Processors.Tracking.TrackingBox import TrackingBox
from Common.CommonHelper import CommonHelper

class TrackingProcessor(PipelineShotProcessor):

    def __init__(self, isDebug=False):
        super().__init__("TRAC")
        self.boxes_last = []
        self.helper = CommonHelper()
        self.isDebug = isDebug

    def ProcessItem(self, pShot: PipelineShot, ctx: dict):
        super().ProcessItem(pShot, ctx)
        pShots = ctx['data']
        meta = self.CreateMetadata(pShot)
        shot = pShot.Shot
        boxes = list(self.GetTrackingBoxes(pShot))

        prevPShot = self.GetPreviousShot(pShot, pShots)
        if not prevPShot:
            for id, box in enumerate(boxes):
                meta[box.id] = {}
                meta[box.id]['object_id'] = id
                box.object_id = id
                self.log.debug(f"Draw box: {box}")
                box.DrawStartPoint(shot.GetImage())
            return
        boxes_last = list(self.GetTrackingBoxes(prevPShot))

        boxes = self.MatchObjects(boxes, boxes_last)

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

    def MatchObjects(self, boxes: [], boxes_prev: []) -> []:
        new_boxes = [] # collect new boxes with order like 'boxes_prev' based on best matched 
        coeffs = np.zeros((len(boxes), len(boxes_prev))) # coeff matrix: rows x columns

        for i, b in enumerate(boxes):
            for j, b_prev in enumerate(boxes_prev):
                coeffs[i][j] = b_prev.GetMatchingCoeff(b)

        for _ in boxes:
            #with np.printoptions(precision=3, suppress=True):
            #    self.log.debug(f"Matching Coeffs matrix: \n{pd.DataFrame(coeffs)}")
            headers = [b.id for b in boxes]
            headers.insert(0, "Prev\Curr") # for first column with boxes IDs
            rows = [b.id for b in boxes_prev]
            matrix = np.c_[rows, coeffs]
            self.log.debug(f"Matching Coeffs matrix: \n" 
                + f"{tabulate(matrix, headers, tablefmt='orgtbl', floatfmt='.2f')}")

            max = np.amax(coeffs)
            pos = np.where(coeffs == max)
            i = pos[0][0]
            j = pos[1][0]
            box = boxes[j]
            box_prev = boxes_prev[i]
            self.log.debug(f"Max: '{max:.2f}' position: {i}x{j}. Write Object_ID: {box_prev}=>{box}")
            box.object_id = box_prev.object_id # match
            new_boxes.append(boxes[i])
            coeffs[i, :] = 0.0
            coeffs[:, j] = 0.0
            # coeffs = np.delete(coeffs, i, 0) # remove row i
            # coeffs = np.delete(coeffs, j, 1) # remove column j

        return new_boxes

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