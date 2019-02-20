import unittest
import json
import threading
import logging
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
        self.logger = logging.getLogger("TEST")
        self.logger.info('start: %s', datetime.now())
        self.yolo = YoloContext(self.yoloPath)

    def test_day_lilia_simple(self):
        print('start: {}'.format(datetime.now()))
        temp = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_simple'
        shots = ThreeShots.FromDir(None, temp)
        shots.yoloContext = self.yolo
        analyseData = shots.Analyse()
        #shots.Show()
        print(json.dumps(analyseData.__dict__, indent=4))
        pprint(analyseData.__dict__, indent=4)
        self.assertIsNotNone(analyseData)


if __name__ == '__main__':
    unittest.main()