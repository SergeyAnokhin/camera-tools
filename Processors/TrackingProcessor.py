import cv2, logging
import pprint as pp
from Pipeline.Model.ProcessingResult import ProcessingResult

class TrackingBox:
    def __init__(self):
        id = 0
        image = []

class TrackingProcessor:
    Shots: []

    def __init__(self):
        self.log = logging.getLogger("PROC:TRAC")

    # def calc_compare(img1, img2):
    #     arr1 = cv2.imread(img1,cv2.IMREAD_COLOR)
    #     arr2 = cv2.imread(img2,cv2.IMREAD_COLOR)
    #     #print(f"Array: {len(arr1)}x{len(arr1[0])}x{len(arr1[0][0])}")
    #     hist1 = cv2.calcHist([arr1],[0],None,[256],[0,256])
    #     hist2 = cv2.calcHist([arr2],[0],None,[256],[0,256])
    #     result = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    #     #print(f"HIST: {img1}=>{img2}: {result}")

    #     arr1 = cv2.imread(img1,cv2.IMREAD_GRAYSCALE)
    #     arr2 = cv2.imread(img2,cv2.IMREAD_GRAYSCALE)
    #     match = cv2.matchTemplate(arr1, arr2, cv2.TM_CCOEFF_NORMED)
    #     print(f'TEMP: {img1}=>{img2}:', max(map(max, match)))

    def Process(self, resultDict: {}):
        result = ProcessingResult()
        yoloSummary = resultDict['YoloObjDetectionProcessor'].Summary
        
        boxes_last = []

        for i in range(len(self.Shots)):
            box_index = 0
            boxes_current = []
            shot = self.Shots[i].Copy()
            print("===", shot.filename, "===")
            summary = yoloSummary[i]
            #pp.pprint(summary)
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
                text = f'box: {box_index}'
                cv2.rectangle(shot.image, pos_left_top, pos_right_bottom, color, 2)
                cv2.putText(shot.image, text, pos_text, cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)

                boxes_current.append(box)
                box_index += 1
                bestMatched = self.CompareBox(boxes_last, box)
                if bestMatched != None:
                    cv2.line(shot.image,bestMatched.center,box.center,(255,0,0),5)

            boxes_last = boxes_current
            result.Shots.append(shot)
        return result

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
            print(f'==MAX MATCH: B{box_last.id} vs B{template.id} = T:{matchTemp:.2f} = H:{hist:.2f} = C:{compCoeff:.2f}')
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
