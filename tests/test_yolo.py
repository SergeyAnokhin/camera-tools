import unittest
import json
import threading
import logging
import jsonpickle
from pprint import pprint
from datetime import datetime
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext

class YoloTest(unittest.TestCase):
    yoloPath = '../camera-OpenCV-data/weights/yolov3-tiny'
    #yoloPath = '../camera-OpenCV-data/weights/yolo-coco'

    def __init__(self, *args, **kwargs):
        super(YoloTest, self).__init__(*args, **kwargs)
        logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', 
            level=logging.DEBUG, datefmt='%H:%M:%S')
        self.log = logging.getLogger("TEST")
        self.log.info('start %s: %s', __name__, datetime.now())
        self.yolo = YoloContext(self.yoloPath)

    def test_day_lilia_simple(self):
        temp = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_simple'
        shots = ThreeShots.FromDir(None, temp)
        shots.yoloContext = self.yolo
        analyseData = shots.Analyse()
        #shots.Show()
        self.log.info(analyseData)
        self.assertIsNotNone(analyseData)
        self.log.info(analyseData.images)
        self.assertIsNotNone(analyseData.images)
        self.log.info(analyseData.images[0])
        self.assertIsNotNone(analyseData.images[0].objects)


# if __name__ == '__main__':
#     unittest.main()