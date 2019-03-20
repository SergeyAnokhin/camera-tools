import cv2
import pprint as pp
from Pipeline.Model.ProcessingResult import ProcessingResult

class TrackingProcessor:
    Shots: []

    def __init__(self):
        pass

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
        for i in range(len(self.Shots)):
            shot = self.Shots[i]
            print("===", shot.filename, "===")
            summary = yoloSummary[i]
            pp.pprint(summary)
            (x, y) = summary['center_coordinate']
            (w, h) = summary['size']
            result.Shots.append(shot)
        return result