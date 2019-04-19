import cv2, logging
import numpy as np
from scipy.spatial import distance
import pprint as pp
from Pipeline.Model.PipelineShot import PipelineShot
from Processors.Processor import Processor

class TrackingBox:
    def __init__(self):
        id = 0
        image = []

class TrackingProcessor(Processor):

    def __init__(self):
        super().__init__("TRAC")
        self.boxes_last = []

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        super().ProcessShot(pShot, pShots)
        pShot.Metadata['TRAC'] = {}
        box_index = 0
        boxes_current = []
        shot = pShot.Shot
        summary = pShot.Metadata['YOLO']
        for box_data in summary:
            (x, y) = box_data['center_coordinate']
            (w, h) = box_data['size']

            box_size = 10
            pos_left_top = (x - box_size // 2, y - box_size // 2)
            pos_right_bottom = (x + box_size // 2, y + box_size // 2)
            box = TrackingBox()
            box.image = self.ExtractBox(shot.image, box_data)
            box.id = box_index
            box.center = (x, y)

            color = 128
            pos_text = (x, y - 5)
            angle = 0
            dist = 0

            boxes_current.append(box)
            box_index += 1
            bestMatched = self.CompareBox(self.boxes_last, box)
            if bestMatched != None:
                cv2.line(shot.image,bestMatched.center,box.center,(255,0,0),3)
                (x, y) = bestMatched.center
                pos_left_top = (x - box_size // 2, y - box_size // 2)
                pos_right_bottom = (x + box_size // 2, y + box_size // 2)
                cv2.rectangle(shot.image, pos_left_top, pos_right_bottom, color, 1)
                box.id = bestMatched.id
                angle = self.angle(box.center, bestMatched.center)
                dist = distance.euclidean(box.center, bestMatched.center)
                pShot.Metadata['TRAC'][box.id] = {}
                pShot.Metadata['TRAC'][box.id]['distance'] = int(dist)
                pShot.Metadata['TRAC'][box.id]['angle'] = int(angle)

            text = f'box: ID{box.id}'
            cv2.rectangle(shot.image, pos_left_top, pos_right_bottom, color, 1)
            cv2.putText(shot.image, text, pos_text, cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2)

        self.boxes_last = boxes_current

    def angle(self, p0, p1=np.array([0,0]), p2=None):
        ''' compute angle (in degrees) for p0p1p2 corner
        Inputs:
            p0,p1,p2 - points in the form of [x,y]
        '''
        if p2 is None:
            p2 = p1 + np.array([1, 0])
        v0 = np.array(p0) - np.array(p1)
        v1 = np.array(p2) - np.array(p1)

        angle = np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1))
        return np.degrees(angle)

    def ExtractBox(self, image, box_data):
        (x, y) = box_data['center_coordinate']
        (w, h) = box_data['size']

        return image[(y - h // 2):(y + h // 2),(x - w // 2):(x + w // 2)]

    def CompareBox(self, boxes_last: [], template: TrackingBox):
        if len(boxes_last) == 0:
            return

        coeffs = []
        for box_last in boxes_last:
            box_resized = self.ResizeForBiggerThanTemplate(box_last.image, template.image)
            # print(f'Resize: {box_last.shape} => {box_resized.shape}')
            # print(f'Template size: {template.shape}')
            matchTempArr = cv2.matchTemplate(box_resized, template.image, cv2.TM_CCOEFF_NORMED)
            matchTemp = max(map(max, matchTempArr))

            hist1 = cv2.calcHist([box_last.image],[0],None,[256],[0,256])
            hist2 = cv2.calcHist([template.image],[0],None,[256],[0,256])
            hist = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

            compCoeff = matchTemp * 0.2 + hist * 0.8
            print(f'==MATCH: B{box_last.id} vs B{template.id} = T:{matchTemp:.2f} = H:{hist:.2f} = C:{compCoeff:.2f}')
            coeffs.append(compCoeff)

        maxValue = max(coeffs)
        maxIndex = coeffs.index(maxValue)
        return boxes_last[maxIndex]
        
    def ResizeForBiggerThanTemplate(self, image, template):
        factors = [x/y for x, y in zip(template.shape[0:2], image.shape[0:2])]
        #print('>fact: ', factors)
        zoom = max(factors)
        zoom = zoom if zoom > 1 else 1
        #print('>Zoom: ', zoom)
        imageResized = cv2.resize(image, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
        return imageResized
